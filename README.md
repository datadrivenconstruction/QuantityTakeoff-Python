# Free Python QTO - QuantityTakeoff 

The free tool QuantityTakeoff allows you to group elements from Revit and IFC models (in BIMJSON-CSV format) with just a few filters and find the required volume values for the grouped elements.

Open App:
http://qto.bimopensource.com/

### Screenshots
![enter image description here](https://opendatabim.io/wp-content/uploads/2021/12/ezgif.com-gif-maker-1.gif)


  QuantityTakeoff is the main tool after the design phase. Creation of such groups allows the quantity surveyor to quickly and without additional tools find the required volume values for the selected elements with the help of filters 
### Screenshots
![enter image description here](https://opendatabim.io/wp-content/uploads/2021/12/qtos.png)



## Built With

-   [Dash](https://dash.plot.ly/)  - Main server and interactive components
-   [Plotly Python](https://plot.ly/python/)  - Used to create the interactive plots


## Requirements

We suggest you to create a separate virtual environment running Python 3 for this app, and install all of the required dependencies there. Run in Terminal/Command Prompt:

```
git clone https://github.com/OpenDataBIM/QuantityTakeoff-Python.git
cd QuantityTakeoff-Python
python3 -m virtualenv venv

```

In UNIX system:

```
source venv/bin/activate

```

In Windows:

```
venv\Scripts\activate

```

To install all of the required packages to this environment, simply run:

```
pip install -r requirements.txt

```

and all of the required  `pip`  packages, will be installed, and the app will be able to run.

## [](https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-manufacture-spc-dashboard#how-to-use-this-app)How to use this app

Run this app locally by:

```
python index.py

```

Open  [http://0.0.0.0:3000/](http://0.0.0.0:3000/)  in your browser, you will see a live-updating dashboard.

