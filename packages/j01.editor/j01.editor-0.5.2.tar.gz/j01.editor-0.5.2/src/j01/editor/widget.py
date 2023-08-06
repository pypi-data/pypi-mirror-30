###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Widgt mixin classes shared in form and jsform

$Id: widget.py 4808 2018-04-09 13:20:14Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
# import zope.i18nmessageid

import z3c.form.widget
import z3c.form.interfaces

import j01.form.widget.textarea

import j01.editor.util
from j01.editor import interfaces


################################################################################
#
# editor

WIDGET = """<div id="%(id)sEditorWrapper" class="j01EditorWrapper">
  <input type="hidden" id="%(id)sWidget" name="%(name)s" value="%(content)s" />
  <div class="j01EditorWrapper">
    <div id="%(id)sEditor">%(html)s</div>
  </div>
</div>
"""


JAVASCRIPT = """<script>
var %(id)sWidget = $('#%(id)sWidget');
var %(id)sEditor = new Quill('#%(id)sEditor', {%(options)s
});
%(id)sEditor.on('text-change', function() {
    %(id)sWidget.val(%(id)sEditor.root.innerHTML);
});
</script>
"""

def getModules(data):
    """Setup Module options"""
    lines = []
    append = lines.append
    for key, value in data.items():
        if key == 'toolbar':
            grps = []
            for grp in value:
                btns = []
                for btn in grp:
                    if isinstance(btn, str):
                        btns.append(btn)
                    elif isinstance(btn, dict):
                        for k, v in btn.items():
                            if isinstance(v, basestring):
                                v = '%s' % v
                            elif v is True:
                                v = 'true'
                            elif v is False:
                                v = 'false'
                            btns.append({k:v})
                grps.append(btns)
            append("\n    %s: %s" % (key, grps))
        elif value is True:
            append("\n    %s: true" % key)
        elif value is False:
            append("\n    %s: false" % key)
        elif value is None:
            append("\n    %s: null" % key)
        elif isinstance(value, int):
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, str):
            if value.startswith('$'):
                append("\n    %s: %s" % (key, value))
            else:
                append("\n    %s: '%s'" % (key, value))
        else:
            append("\n    %s: %s" % (key, value))
    return ','.join(lines)

def getJavaScript(data):
    """EditorWidget JavaScript generator."""
    try:
        id = data.pop('id')
    except KeyError, e:
        id = 'j01Editor'

    lines = []
    append = lines.append
    for key, value in data.items():
        if key == 'modules':
            if value is None:
                continue
            append("\n        %s: {%s}" % (key, getModules(value)))
        # if key == 'toolbar':
        #     grps = []
        #     for grp in value:
        #         btns = []
        #         for btn in grp:
        #             if isinstance(btn, str):
        #                 btns.append(btn)
        #             elif isinstance(btn, dict):
        #                 for k, v in btn.items():
        #                     if isinstance(v, basestring):
        #                         v = '%s' % v
        #                     elif v is True:
        #                         v = 'true'
        #                     elif v is False:
        #                         v = 'false'
        #                     btns.append({k:v})
        #         grps.append(btns)
        #     append("\n    modules: {%s: %s}" % (key, grps))
        elif value is True:
            append("\n    %s: true" % key)
        elif value is False:
            append("\n    %s: false" % key)
        elif value is None:
            append("\n    %s: null" % key)
        elif isinstance(value, int):
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, str):
            if value.startswith('$'):
                append("\n    %s: %s" % (key, value))
            else:
                append("\n    %s: '%s'" % (key, value))
        else:
            append("\n    %s: %s" % (key, value))
    code = ','.join(lines)
    return JAVASCRIPT % {
            'id': id,
            'options': code,
        }


class EditorWidget(j01.form.widget.textarea.TextAreaWidget):
    """Editor widget"""

    zope.interface.implementsOnly(interfaces.IEditorWidget)

    value = u''

    theme = 'snow'
    toolbar =  [
        ['bold', 'italic'],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
        ['clean'],
    ]

    def cleanup(self, value):
        """Cleanup method which removes any tag attribute and only allows a
        small set of tags. See simpleHTML for more info.
        """
        return j01.editor.util.simpleHTML(value)

    def extract(self, default=z3c.form.interfaces.NO_VALUE):
        """Support cleanup value call"""
        value = super(EditorWidget, self).extract(default)
        if value is not z3c.form.interfaces.NO_VALUE:
            # cleanup if value is given
            value = self.cleanup(value)
        return value

    @property
    def modules(self):
        data = {}
        if self.toolbar is not None:
            data['toolbar'] = self.toolbar
        return data

    @property
    def javascript(self):
        return  getJavaScript({
            'id': self.__name__,
            'theme': self.theme,
            'modules': self.modules,
            })

    def update(self):
        # add javascript marker, usable for load javascript
        self.request.annotations['j01.editor.widget.EditorWidget'] = True
        super(EditorWidget, self).update()

    def render(self):
        """See IBrowserWidget."""
        value = self.value
        if not value:
            value = u''
        widget = WIDGET % {
                'id': self.__name__,
                'name': self.name,
                'content': j01.editor.escape(value),
                'html': value
            }
        return '%s\n%s' % (widget, self.javascript)


def getEditorWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return z3c.form.widget.FieldWidget(field, EditorWidget(request))
