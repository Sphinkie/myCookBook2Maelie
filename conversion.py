# coding: UTF-8
# ==================================================================
# Conversion de recettes de MyCookBook vers Mealie
# ==================================================================
# David de Lorenzo (2023)
# ==================================================================

import json
import xml.etree.ElementTree as ET
import tempfile          # This module creates temporary files and directories
import zipfile           # This module provides tools to create, read, write, append, and list a ZIP file.
from pathlib import Path # Ce module offre des classes représentant le système de fichiers.


# =============================================================================
# 
# =============================================================================
class conversion:

    tags = {}            # Dictionnaire contenant les informations d'une recette
    tempdir = Path(".")
    image_name = ""
    tagNames = {         # "MCB_label":"NextCloud_label"
        "title":"name",
        "preptime":"prepTime",
        "cooktime":"cookTime",
        "totaltime":"totalTime",
        "quantity":"recipeYield",
        "description":"description",       # multiline
        "ingredient":"recipeIngredient",   # multiline
        "recipetext":"recipeInstructions", # multiline
        "category":"recipeCategory",
        "url":"url",
        "imagepath":"image",
        "imageurl":"imageUrl",
        "source":"author",           # multiline
        "video":"video",             # not used
        "rating":"aggregateRating",  # cas particulier
        "comments":"comments"        # ????
    }

    # ------------------------------------------------------------------------------------------
    # On parse le fichier MyCookBook dans un Element Tree
    # ------------------------------------------------------------------------------------------
    def __init__(self,filename):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            self.tempdir = tmpdir 
            print (tmpdir)
        recipes_tree = self.importer(filename)
        self.parse(recipes_tree)
		# Generate a new zip file
        directory = Path(self.tempdir, "myCookBook")
        with zipfile.ZipFile("output/myCookBook.NextCloud.zip", mode='w') as archive:
            for file_path in directory.rglob("*"):
                archive.write(file_path, arcname=file_path.relative_to(directory) )
        print ('done')


    # ------------------------------------------------------------------------------------------
	# Unzip file into temporary directory
    # ------------------------------------------------------------------------------------------
    def importer(self, filename):
			# Open the zip file
            with zipfile.ZipFile(filename) as zipped_file:
				# Extract all in the temporary directory
                zipped_file.extractall(self.tempdir)
				# on recupère le fichier XMl contenant toutes les recettes
                extracted_xml = Path(self.tempdir)/"mycookbookrecipes.xml"
                print (extracted_xml)
                with open(extracted_xml, encoding="utf-8") as xml_flow:
                    recipes_tree = ET.parse(xml_flow)
                    return recipes_tree
 
	# ------------------------------------
    # Analyse des données (1 by 1) and export 1 json file per recipe.
    # Move the images to the new folder
    # ------------------------------------
    def parse(self, recipes_tree) -> None:
        recipe_number=0           # Compteur
        recipes_root = recipes_tree.getroot()
        for recipe in recipes_root.findall("recipe"):
         	# For each recipe
            # Create a new JSON file with header
            self.createNewJson();
            for child in recipe:
                self.addTag(child)
            # the json file where the output must be stored
            output_path = Path(self.tempdir + F"/mycookbook/recipe_00{recipe_number}" )
            output_file = Path(output_path , "recipe.json")
            output_file.parent.mkdir(exist_ok=True, parents=True)
            output_file.open('w')
            json_string = json.dumps(self.tags, indent=6)
            output_file.write_text(json_string)
            self.exportImage(output_path)
            recipe_number+=1

    # ------------------------------------
    # Move the image to the output path
    # ------------------------------------
    def exportImage(self, output_path):
        if self.image_name == "": return
        source_file = Path(self.tempdir, self.image_name)
        source_ext = self.image_name[-3:]
        dest_path = str(output_path) + F"/full.{source_ext}"
        source_file.rename(dest_path)

    # ------------------------------------
    # Add a tag to the recipe
    # ------------------------------------
    def addTag(self, balise):
        # print(balise.tag, balise.text)
        # We jump the tags without correspondance
        if self.tagNames.get(balise.tag) == None: return
        # On traite les cas particuliers:
        if balise.tag == "rating":
            # RATING
            self.tags["aggregateRating"] = {"@type": "AggregateRating", 
                                            "ratingValue": balise.text if not None else 0,
                                            "ratingCount": "1"}
        elif balise.tag == "source":
            # SOURCE / AUTHOR (only the 1st line)
            self.tags["author"] = {"@type": "Person", 
                                   "ratingValue": balise.find("li").text if not None else "Anonymous"}
        elif balise.tag in ["description","ingredient","recipetext"]:
            # Multiline fields
            lignes = []
            for ligne in balise:
                if ligne.text is not None: lignes.append(ligne.text)
            self.tags[self.tagNames.get(balise.tag)] = lignes
        else:
            # We jump the empty tags
            if balise.text == None: return
            # On ajoute au dictionnaire (Tag names should be renamed)
            self.tags[self.tagNames.get(balise.tag)] = balise.text
            if balise.tag == "imagepath": self.image_name = balise.text
            if balise.tag == "title": print(balise.text)
        
    # ------------------------------------
    # Initiate a new Json file
    # ------------------------------------
    def createNewJson(self):
        self.tags.clear()
        self.image_name = ""
        # print(balise.tag, balise.text)
        self.tags["@context"] = "http:\/\/schema.org"
        self.tags["@type"] = "Recipe"


# ----------------------------------------------------------------------------
# Test
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    conversion('input\mycookbookrecipes.mcb')