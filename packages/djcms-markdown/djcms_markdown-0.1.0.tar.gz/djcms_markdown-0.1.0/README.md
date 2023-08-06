# djcms_markdown

This is a Django CMS Plugin to port Ghost Markdown editor, based in:
* [cmsplugin-markdown](https://github.com/bitlabstudio/cmsplugin-markdown)
* [Ghost-Markdown-Editor](https://github.com/timsayshey/Ghost-Markdown-Editor)
* [Easy markdown and syntax highlighting in Django](https://www.ignoredbydinosaurs.com/posts/275-easy-markdown-and-syntax-highlighting-django)

#### Demo
![Editor](https://cdn.rawgit.com/carlosmart626/djcms_markdown/master/media/editor.gif)

Support:

* Live editing
* Live preview
* Code snippets

## Instalation

```bash
pip install djcms_markdown
```

## Usage
In `settings.py`

```python
INSTALLED_APPS = (
    # ...
    'djcms_markdown',
)
```
Add defult code styles:

```
p code {
    font-family: Consolas,Menlo,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New,monospace,sans-serif;
    background: #282a36;
    color: #ececec;
    vertical-align: middle;
    white-space: pre-wrap;
    font-size: 0.8em;
    line-height: 1em;
    border-radius: 4px 4px 4px 4px;
    -moz-border-radius: 4px 4px 4px 4px;
    -webkit-border-radius: 4px 4px 4px 4px;
    border: 1px solid #303030;
    padding: 0.2rem 0.3rem 0.1rem;
}
```

## Using highlight.js
![Editor](https://cdn.rawgit.com/carlosmart626/djcms_markdown/master/media/code_example.png)
Add to your template:

**styles**
```
<link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/styles/dracula.min.css">
```
More style in highlight.js [repo].(https://github.com/isagalaev/highlight.js/tree/master/src/styles)

**highlight.js**
```
<script src="//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/highlight.min.js"></script>
```
**highlight.js init**
```
<script>
    $(document).ready(function () {
        $('pre code').each(function (i, block) {
            hljs.highlightBlock(block);
        });
    });
</script>
```

## Contributing
```
python setup.py test
```