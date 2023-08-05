import os
import yaml
from jinja2 import Environment, FileSystemLoader

# Function to render template from template environment and context
def render_template(template_filename, context):
    # Set up template environment from "templates" folder
    PATH = os.path.dirname(os.path.abspath(__file__))
    TEMPLATE_ENVIRONMENT = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(PATH, 'data')),
        trim_blocks=False)
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def yaml_to_md(input_name, output_name, template_name):
    """
    [yaml_to_md] takes three file names: <input>, <output>, <template>
    """
    # Declare output file and parameters
    context = yaml.load(open('data/' + input_name))

    # Final render
    with open('data/' + output_name, 'w') as f:
        output = render_template(template_name, context)
        f.write(output)

def md_to_pdf(input_filename, output_filename):
    """
    md_to_pdf converts input_filename file to pdf,
    and the name of the pdf file is output_filename

    Parameters
    ----------
    input_filename : string
    name of file to convert to pdf

    output_filename : string
    name of the pdf file

    """

    os.system("pandoc " + input_filename + " -o " + output_filename + ".pdf" )

def docx_to_md(input_filename, output_filename):
    """
    docx_to_md converts input_filename file to md,
    and the name of the md file is output_filename

    Parameters
    ----------
    input_filename : string
    name of file to convert to pdf

    output_filename : string
    name of the pdf file

    """

    os.system("pandoc -s " + input_filename + " -t markdown -o " + output_filename + ".md" )
