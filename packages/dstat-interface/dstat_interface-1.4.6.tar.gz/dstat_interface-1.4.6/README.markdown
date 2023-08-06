##### _DStat is described in detail in [Dryden MDM, Wheeler AR (2015) DStat: A Versatile, Open-Source Potentiostat for Electroanalysis and Integration. PLoS ONE 10(10): e0140349. doi: 10.1371/journal.pone.0140349](http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0140349) If you use this information in published work, please cite accordingly._
---

This is the documentation for the DStat interface software.
The DStat interface is written primarily in Python and runs on Linux, Mac, and Windows.
It is the main method for running experiments on the DStat, controlling experimental parameters and collecting and plotting data.
It currently has no abilities for analyzing recorded data or opening previously saved data files, but data is saved in a simple text format or numpy-compatible binary format and plots can be saved as images.

## Table of Contents:

1. [Installation](#Installation)
	1.  [MacOS](#macos)
	    1.  [Using Anaconda (Recommended)](#using-anaconda-recommended)
	    2.  [Old Homebrew Instructions](#old-homebrew-instructions)
    1.  [Linux](#linux)
    2.  [Windows](#windows)
    3.  [Upgrading](#upgrading)
2. [Getting Started](#Getting-Started)

# Introduction
The DStat interface is written primarily in Python and runs on Linux, Mac, and Windows.
It is the main method for running experiments on the DStat, controlling experimental parameters and collecting and plotting data.
It currently has no abilities for analyzing recorded data or opening previously saved data files, but data is saved in a simple text format and plots can be saved as images.

# Installation

dstat-interface has moved to gtk+3 and we now recommend Anaconda/Miniconda for installation.

## MacOS
### Using Anaconda (Recommended)

  1. [Install Miniconda](https://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh) It doesn't matter if you pick Python 2.7 or 3.5—this just sets Miniconda's default Python. (Skip if Miniconda or Anaconda are already installed)
  
  2. Create a new environment for dstat. In a terminal type:
````conda create -n dstat -c mdryden python=2.7 dstat-interface dstat-interface-deps````

  3. Then to run dstat-interface:
    ````source activate dstat
    python -m dstat_interface.main````

#### Old Homebrew Instructions
The easiest way to get most of the necessary requirements to run dstat-interface is using [Homebrew](http://brew.sh):

```shell
brew tap homebrew/python
brew update
brew install python gobject-introspection gtk+3 pygobject3 py2cairo scipy zeromq 
brew install matplotlib --with-pygtk
```

Be patient on the last step—matplotlib needs to be compiled and may take 2 or 3 minutes.

Make sure you're using brew-installed python, not OS X's default python. `which python` should point to `/usr/local/bin/python` not `/usr/bin/python`. Type `brew doctor` for more information if you are having issues.

The final requirements, can be installed using python's pip system:

    pip install pandas pyserial pyzmq pyyaml seaborn zmq-plugin

## Linux
Linux prerequisite installation is similar to that of MacOS with Homebrew, only using your distribution's native package manager rather than Homebrew, and X11 will likely be installed already. Some distributions may not have packages available for installing matplotlib or numpy, in which case, they should be installed using pip.

These instructions were tested on Ubuntu 17.04:

````shell
sudo apt-get install gobject-introspection python-gobject python-pip
pip install dstat-interface
````

You will need to add your user to the `dialout` group to access virtual serial ports (replace <user> with your username):

```shell
sudo usermod -a -G dialout <user>
```

## Windows
The following terminal commands will result in a full installation of dstat-interface and its requirements, assuming [64-bit Miniconda][1] is installed:

```shell
conda create -n dstat -c mdryden python=2 dstat-interface
activate dstat
```

To finish the installation, GTK+3 and its Python bindings must be installed:

  1. Download the latest all-in-one installer from [here][2].
  
  2. When the installer prompts for the path to your Python distribution, navigate to your Miniconda/Anaconda envs folder and choose the dstat folder. If you chose to install Miniconda for your user only, the envs folder is found in `$USER/Miniconda2/envs` (for Miniconda) or `$USER/Anaconda/envs` (for Anaconda), where `$USER` is your user directory. If you installed Miniconda for all users, the Miniconda2/Anaconda folder will be in the root of your C: drive.
  
  3. When the installer asks which modules to install, choose GTK.
  
  4. Finish the installer.

We are installing in a separate environment to keep a clean system.
`activate dstat` will enter the environment (must be done whenever a new terminal is opened),
and `deactivate` will return to the root environment.

Therefore, to run dstat-interface from our environment, we must first activate it (if not already done) before launching it:

```shell
activate dstat
python -m dstat_interface.main
```

[1]: https://repo.continuum.io/miniconda/Miniconda2-latest-Windows-x86_64.exe
[2]: https://sourceforge.net/projects/pygobjectwin32/

## Upgrading

Anaconda builds can be upgraded to the latest version by issuing this command (from an activated conda environment):

```shell
conda upgrade -c mdryden dstat-interface  # For MacOS, be sure to upgrade dstat-interface-deps as well
```

pip installs can be upgraded similarly:

```shell
pip install --upgrade dstat-interface
```

You can also run development builds directly from a cloned git repository (from an activated conda environment):

```shell
cd ~/src/dstat-interface/dstat_interface # Replace with path to dstat_interface folder inside repository
python -m main
```

# Getting started
## Interface overview

![Main interface](images/1.png)

1. Menu bar
	![Menu bar](images/5.png)
	* File
		* Save Current data… — Saves the data of the currently visible plot as a space-separated text file or numpy .npy file
		* Save Plot… – Save the currently visible plot as a .pdf
		* Quit — Quits dstat-interface
	* Dropbot
		* Connect — Listens for µDrop connection over ZMQ
		* Disconnect — Disconnect from µDrop
	* Help
		* About — Displays license information
2. ADC Settings Panel
	* PGA Setting — Sets the ADC's internal voltage gain. Should almost always be left at 2x except for potentiometry as increasing voltage gain reduces S/N. Settings other than 2x do not adjust data to match (e.g. one must halve measured current/voltage values if PGA is set to 4x).
	* Sample Rate - Sets the ADC's sample frequency. Lower rates give less noise, but reduced temporal resolution. Digital filter has a zero at multiples of the sample rate, so the Sample Rate setting can be used to filter out AC line noise by setting the rate to a factor of the line frequency, e.g. for 60 Hz rejection, choose 60, 30, 15, 10, 5, or 2.5 Hz.
	* Input Buffer — Sets the ADC's internal input buffer. Should generally be enabled.
3. Potentiostat Settings Panel
	* Gain — Controls the current-to-voltage converter gain. Higher values produce better S/N but reduce full scale current limit. Has no effect on potentiometry experiments.
4. Experiment Panel - Pulldown menu changes between experiment types and parameters are entered below.
5. Experiment Control
	* Execute — Start the currently selected experiment with the given parameters.
	* Stop — Stop the currently running experiment. If Autosave is enabled, the partial experiment will be saved.
6. Communications Panel
	* Serial Port — Select the port where DStat is located. On Windows, this is generally something like `COM3`. On Mac OS X, it should appear as `/dev/cu.usbmodem12...E1`. On Linux, it may vary, but will start with `/dev`. If you're not sure, the simplest way is to check the list before and after plugging the DStat in. (Clicking the Refresh button after)
	* Refresh — Refreshes the Serial Port list
	* Connect — Attempts to handshake with DStat. If unsuccessful, it will time out after approximately 30 seconds.
	* OCP — Displays the current open circuit potential measured at the reference electrode input. Active when DStat is connected and an experiment is not running.
	* Status bar — Displays status and error messages.
7. Data display tabs — Switches between the plot and raw data tabs
	* Plot — Displays the graphical representation of the incoming data.
	* Raw Data — The raw experiment data. Doesn't appear until the experiment is complete. The first column corresponds to the x-axis of the plot (time or voltage), and the second column corresponds to the y-axis (current or voltage). For mult-scan experiments, additional pairs of columns represent successive scans.
	![raw data](images/4.png)
	* Extra Data — For SWV and DPV, the separate forward and reverse currents are recorded here.
8. Autosave controls
	* Autosave — Enables automatic data saving on experiment completion. A text data file and a .pdf image of the plot will be saved.
	* File save location
	* File name selector — A number will be appended automatically if a file with the same name already exists.
9. Plot display
10. Plot navigation controls — For changing the view of the data plot.

## Connecting to DStat

1. Plug the DStat into a USB port, ensuring that drivers are loaded correctly on Windows systems.
2. Click Refresh in the Communications Panel to refresh the Serial Port list and choose the correct entry for the DStat (described above).
3. Click Connect.
4. If the connection was successful, a number should appear in the OCP field and the version number will appear in the status bar.
![connect](images/2.png)

If the connection failed, unplug the DStat and try again.

## Running an experiment

1. Choose the experiment you want to run in the Experiment Panel.
2. Fill the parameter fields.
3. Set an appropriate potentiostat gain.
4. Click Execute.

![experiment](images/3.png)
