# AguaClara AIDE Document

This is a tool for combining .yaml data files with Markdown templates via the Jinja2 templating engine to produce complete Markdown/.pdf files.

# Installation Instructions

## Installing `aide_document`

### Via `git`

1. Ensure that you have `git` installed by running `git --version`. If you don't have it, [get it here](https://git-scm.com/downloads "Git Installation") and configure it [using these instructions](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup "Git Configuration").
2. Run `git clone https://github.com/AguaClara/aide_document.git` in the location of your choice.

If you choose to install via `git`, be sure to put the `aide_document/aide_document` subfolder in the same directory as the files that utilize the package.

### Via `pip`

**NOTE: the current `pip` installation is nonfunctional at this time. Please `git clone` this repository for the time being.**

1. Ensure that you have `pip` installed by running `pip -V`. `pip` comes with Python 2 >=2.7.9 or Python 3 >=3.4, but if you don't have it, [follow these instructions](https://pip.pypa.io/en/stable/installing/ "Pip Installation Instructions").
2. Run `pip install aide_document --user` anywhere.

## Installing a LaTeX Engine

To convert Markdown to PDF using Pandoc, you must install TeX Live for your operating system. Here are installation files for each OS:
* [Windows](http://mirror.ctan.org/systems/texlive/tlnet/install-tl-windows.exe "Windows TeX Live Installation File")
* [MacOS](http://tug.org/cgi-bin/mactex-download/MacTeX.pkg "MacOS MacTeX Installation File") (Note: this is MacTeX, an optimized variant of TeX Live.)
* [Linux](http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz "Linux TeX Live Installation File")

## Installing Pandoc

Pandoc is required for converting Markdown files to PDF. More detailed instructions can be found [here](https://pandoc.org/installing.html).
* [Windows Installation File](https://github.com/jgm/pandoc/releases/download/2.1.2/pandoc-2.1.2-windows.msi "Windows Pandoc Installation File")
* MacOS: in Terminal, run `brew install pandoc`
* [Linux Installation File](https://github.com/jgm/pandoc/releases/download/2.1.2/pandoc-2.1.2-1-amd64.deb "Linux Pandoc Installation File")
# Using the Package

First, import the package at the top of your file:

```python
from aide_document import convert
```

Within `convert`, there are two methods with self-explanatory functions:
- `yaml_to_md(input_name, output_name, template_name)`
- `md_to_pdf(input_filename, output_filename)`
- `docx_to_md(input_filename, output_filename)`

You can also translate the file on a line by line base:
```python
from aide_document import translate
```

Within `translate`, there is one methods with self-explanatory functions:
- `translate(input_name, source_language, target_language, output_name)`


# About

## Semester Goals

The AIDE Document sub-team's goals for the Spring 2018 semester are to use Jinja2 to parse YAML input and convert it to Markdown/.pdf files conforming to templates provided by AIDE Design.
## Team

| Name           | Role   | Email             |
|----------------|--------|-------------------|
| Matan Presberg | Lead   | mgp64@cornell.edu |
| Kevin Juan     | RA     | kj89@cornell.edu  |
| Karan Newatia  | Member | kn348@cornell.edu |
| Oliver Leung   | Member | oal22@cornell.edu |
| Yilin Lu       | Member | yl668@cornell.edu |

## Reports and Presentations
