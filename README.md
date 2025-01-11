# visa-scraping

This project focuses on the automated collection of information through web scraping techniques. Its greatest importance lies in the generation of automatic alerts when a web page is scraped, allowing users to be more efficient in their use of time and optimize the data monitoring process.

[[_TOC_]]

## Installation

1. It is recommended to use Python 3.11. You can download it from the following link: https://www.python.org/downloads/

2. It is recommended to install in a [**virtual environment**]. Inside the project, you will find the ```PyEnv.bat``` executable, which creates a virtual environment in the project directory and installs everything necessary to run the flow specified in the ```setup.cfg``` file.

## Execution

Before running the project, make sure to activate the virtual environment if you are using one.

To run the main file **execution.py** use the following command:

```
python -m visa_scraping.execution
```

Note: The project includes the executable ```PyRun.bat```, which activates the virtual environment and automatically runs the flow.


## Prerequisites

The project has been generated for Python version
```
3.10
```
. The libraries or packages required for execution are:
- `versioneer>=0.10`
- `setuptools>=75.3.0`
- `openpyxl>=3.1.2`
- `pandas>=2.2.3`
- `beautifulsoup4>=4.12.3`
- `selenium>=4.25.0`


## Inputs and outputs

The inputs used in the process are:

| Input | Description|
| - | - |
| driver_path | Location of the web driver within the project, defined in the global driver_path parameter of the ```config.json``` file. |
| user | Username to access the page, defined in the global user parameter of the ```config.json``` file. |
| password | Access password, defined in the global password parameter of the ```config.json``` file. |
| sender_email | Email from which the notification email will be sent, defined in the global sender_email parameter of the ```config.json``` file. |
| password_email | Password of the email from which the notification email will be sent, defined in the global password_email parameter of the ```config.json``` file. |
| recipient_email | Email to which the notification will be sent, defined in the global parameter recipient_email of the ```config.json``` file. |

If executed on Github, the secrets can and should be modified.

The results obtained are:

| Result| Description|
| - | - |
| execution_log.csv | Result stored in the ```outputs``` folder of the execution in case a date less than the event date is found |
