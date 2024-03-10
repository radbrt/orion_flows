from prefect import task, flow
from prefect import get_run_logger
import os
from prefect.artifacts import create_markdown_artifact
import matplotlib.pyplot as plt



# Step 3: Combine tasks into a full workflow that
#         processes all new data files.
@flow(name="Coiled")
def coiled():

    logger = get_run_logger()
    x = [1, 2, 3, 4, 5]
    y = [1, 4, 9, 16, 25]

    # Plot the data
    plt.figure()
    plt.plot(x, y)
    plt.title('Sample Plot')

    # Save the plot as SVG
    plt.savefig('sample_plot.svg', format='svg')

    with open('sample_plot.svg', 'r') as file:
        svg_content = file.read()

    # Prepare the markdown content
    markdown_content = f"""
# My Markdown Report

Here is a graph:

{svg_content}
"""

    print(markdown_content)
    create_markdown_artifact(markdown_content, "reportmd", "My Markdown Report")

if __name__ == '__main__':
    coiled()


