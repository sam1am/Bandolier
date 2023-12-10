# Self-Assessment Interviews (SAI) Application 📝

![Placeholder Image](./img/placeholder_image.png)

The SAI application 🚀 is a platform designed to facilitate personal self-assessments in various domains, focusing on helping users understand and reflect on their mental and emotional well-being 🧠. It offers a selection of open-source self-assessment interviews, including the newly proposed Impact on Daily Life Depression Inventory (IDL-DI).

## Latest Enhancements ✨

- **Highlighting in Interviews**: Added support for highlighting phrases or sentences within interview questions using the `==highlight==` syntax.
  
- **Consistent Option Numbering**: We've implemented custom logic to ensure that question options are numbered consistently, which aligns with their scoring values to prevent user confusion during interviews.

- **Improved Markdown Rendering**: The application now uses the `rich` library to display Markdown-formatted content in the terminal, enhancing the readability of interview introductions and other textual information.

## Installation 🛠️

Ensure Python 3.x is installed on your system prior to running the SAI application.

> 💡 For **Windows users**, it's recommended to use the Windows Subsystem for Linux (WSL) for an optimal experience.

To install and run the application, follow these steps:

1. Clone or download the SAI repository to your local machine.
2. Navigate to the project's root directory via your terminal or command prompt.
3. Execute `./autorun.sh` to set up the environment, which includes:
   - Creating and activating a Python virtual environment.
   - Installing necessary dependencies from `requirements.txt`.
   - Launching the application.

> 🔗 [WSL Installation Guide](https://docs.microsoft.com/en-us/windows/wsl/install)

## Usage 📖

Upon starting the SAI application, users will encounter a main menu prompting them to select a self-assessment interview. After choosing an interview, the Markdown-formatted introduction or information at the top (under single `#` headers) will be nicely rendered in the terminal, followed by the questions. User responses, scores, and interpretations are shown upon completion and saved for progress tracking.

## New Interviews 🆕

To create a new self-assessment interview, simply:

1. Add a Markdown (.md) file to the `./interviews` folder.
2. Incorporate questions, answer options, and define scoring categories within that file.
3. The new interview will automatically be loaded and ready for use the next time the SAI application runs.

## License (MIT License) 📄

The SAI application, including the IDL-DI content, comes under the MIT License, enabling broad usage, distribution, and contributions.

## Contributions 🤝

We highly encourage community contributions, including new self-assessment interviews, improvements to existing content, translations, and collaborating in research for validation purposes.

## Disclaimer 🚫

Please note that the SAI application and its content, such as the IDL-DI, are not clinically validated and should not be used as substitutes for professional medical advice or treatment. These resources are meant for informational and self-reflection purposes only. It's important for users to consult health professionals regarding any concerns about their mental health.

