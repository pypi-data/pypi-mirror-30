#!/usr/bin/env python3
""" Renders *.asc (asciidoc) files to PDF or HTML then counts pages & words

HTML or other render formats requires asciidoctor` ruby package/cli:

```
$ brew install asciidoctor || gem install asciidoctor
```

PDF rendering requires the ruby package and cli command `asciidoctor-pdf`:

```bash
$ gem install asciidoctor-pdf --pre
```

You probably also want syntax highlighting so:

```
$ gem install rouge
$ gem install pygments.rb
$ gem install coderay
````

You can activate the Rouge syntax highlighter with the following atttribute in your *.asc files:

```asciidoc
:source-highlighter: rouge
```

Usage:

To render a folder `~/src/lane/manuscript/*.asc` files to PDF within a folder named "lane" that has 3 subfolders (`build/`, 'images/` and `manuscript/`):

$ python countpages.py ~/src/lane/manuscript/ pdf


create a symlink (or hard link) in .git/hooks
>>> cd .git/hooks/
# >>> ln -s ../../code/utils/pre-commit
"""

import os
import subprocess
import sys

from traceback import format_exc


nlpia_dir = os.path.dirname(os.path.realpath(__file__))


def shell_quote(s):
    return "'" + s.replace("'", "'\\''") + "'"


if __name__ == '__main__':
    manuscript_dir = os.path.abspath(os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else '.'))
    renderas = (sys.argv[2] if len(sys.argv) > 2 else 'html5').lower().strip()
    renderext = 'html' if renderas == 'html5' else renderas
    os.chdir(manuscript_dir)
    files = os.listdir()
    lane_dir = os.path.dirname(manuscript_dir)
    build_dir = os.path.join(lane_dir, 'build')
    css_path = os.path.join(build_dir, 'manning.css')
    asciidoctor = 'asciidoctor-pdf' if renderas == 'pdf' else 'asciidoctor'

    total_wc, chapters_wc = 0, 0
    for filename in files:
        if filename.lower().endswith('.asc'):
            print("-" * 40)
            print(filename + ':')
            quoted_filename = shell_quote(filename)
            result = subprocess.Popen("wc {}".format(quoted_filename),
                                      shell=True, stdout=subprocess.PIPE)
            try:
                wc = int(result.communicate()[0].split()[1])
                total_wc += wc
                if filename.lower().strip().startswith("'ch"):
                    chapters_wc += wc
                print('  Word count: {}'.format(wc))
                print('  Approximate Pages: {}'.format(int(wc / 400.) + 1))
            except:
                print('  WC SHELL COMMAND FAILED!!!!!')
                print(format_exc())
            html_file_path = os.path.join(build_dir, filename[:-4] + '.' + renderext)
            shellcmd = "{} -a stylesheet={} -b {} -d book -B {} -o {} {}".format(
                asciidoctor, css_path, renderas, shell_quote(manuscript_dir),
                shell_quote(html_file_path), shell_quote(filename))
            print(shellcmd)
            result = subprocess.Popen(shellcmd,
                                      shell=True, stdout=subprocess.PIPE)
            result.wait()  # don't let commit proceed until rendering is done
            try:
                ans = ' '.join(result.communicate()[0])
                print('asciidoctor returned: {}'.format(ans))
            except:
                print('  `asciidoctor` SHELL COMMAND FAILED!!!!!')
                print('  You probably need to `gem install asciidoctor`')

    print('=' * 60)
    print('Total words, pages: {}, {}'.format(total_wc, int(total_wc / 400.) + 1))
    print('Total chapter words, pages: {}, {}'.format(chapters_wc, int(chapters_wc / 400.) + 1))

    shellcmd = "cd {} && git add build/*.{}".format(lane_dir, renderext)
    print(shellcmd)
    result = subprocess.Popen(shellcmd, shell=True, stdout=subprocess.PIPE)
    msg = result.communicate()[0]
    # print('Committed newly-rendered HTML by aciidoctor:')
    # print(msg)
