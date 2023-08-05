# ArcGIS Pro Project Templates

Because there is no known API for creating project templates this build process is manual.  To create the project template you must have ArcGIS Pro 1.4 installed.


- Launch ArcPro
- Create a Blank project
- Name the project ENVIPyManagement
- Open a Map by selecting Insert -> New Map -> New Map.  This is so completed task results will auto display on the map
- In the project pane right-click on Toolboxes and select Add Toolbox.
- select perforce-root/envipy/envipyarc/envipyarc/esri/toolboxes/ENVI Management Tools.pyt
- In Perforce, Checkout the ENVI Management Tools.pyt so you have write access.
- Right-click on ENVI Management Tools and select Edit
- change the line
```python
self.alias = "envi"
```
To
```python
self.alias = "envipro"
```
- Save and exit
- In the ribbon toolbar select Share -> Project Template
- Select Save template to file
- Save in perforce-root/envipy/envipyarc/envipyarc/esri/projecttemplates
- Summary: "ENVI Py Management Tools"
- Tags: "ENVI"
- Select Analyze
- Select Create
- Revert changes to ENVI Management Tools.pyt
- Check in the project template to perforce.

