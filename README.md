# myCookBook2Mealie

Assistant for recipes migration from myCookBook to Mealie

## Purpose

[myCookBook](https://www.cookmate.online/) and [Mealie](https://hay-kot.github.io/mealie/) are two recipe managers, hosted on internet 
with an Android application (and a browser web application) to view and edit your kitchen recipes.

The goal of this tools is to migrate your recipes from myCookBook to Mealie.

## Requisite

Python 3 is needed to execute this tool.

## Operations

For the migration, proceed as follows:

1. From the **myCookBook** web application, go to *Administration* menu, and export all your recipes.
2. You will obtain a file named `mycookbook.mcb` (containing the pictures and the recipies under XML format).
3. Put this file into the `input` folder.
4. Run the `conversion.py` script.
5. A file named `mycookbook.nextcloud.zip` is generated in the `output` folder.
   This file contains the images and the recipes under the json format, witch is recognized by Mealie.
6. Open the **Mealie** web aplication with an *administrator* account, go to the *Parameters* menu, and clic on `Try a migration`
7. Select the **NextCloud** format and import the `mycookbook.nextcloud.zip` file.
8. Wait for 5 to 10 minutes.
9. Go to the **Recipes** menu: you receipes are here!
