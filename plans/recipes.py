
from plans import * 

two_bean_salad = Steps(
    Requirements( 
        Steps(   # Step 1
            Optional(
                Steps(
                    Action("Roll up kaffir leaves"), 
                    Action("Slice as thinly as possible"), 
                    Action("Finely chop the strips")
                )
            ), 
            Action("Zest lime"), 
            Action("Roughly chop 30g cilantro"), 
            Action("Wash and pick mint leaves"), 
            Action("Peel and crush garlic clove"), 
            Action("Measure 1/4 cup olive oil"), 
            Action("Measure 1/2 tsp salt"), 
            Action("Mix into blender"), 
            Action("Blitz until smooth")
        ), 
        Steps (  # Step 2
            Action("Peel edamame"),
            Action("Boil large pan of salted water"), 
            Action("Add green beans and blanch for 3 minutes"), 
            Action("Add edamame for 1 minute"), 
            Action("Drain and refresh under cold water"), 
        )
    ), 
    Steps( # Step 3 
        Action("Squeeze 2 Tb lime juice"), 
        Action("Spoon lime paste over beans"), 
        Action("Add lime juice"), 
        Action("Stir and add black sesame seeds")
    )
)


eqq_square_text = """Preheat the oven to 300ºF. Butter an 8- or 9-inch square baking dish. Bring a pot of water to a boil — I use my electric tea kettle, which holds about 4 cups.

In a large bowl, whisk together the eggs and salt. Add the half-and-half and whisk to combine. Transfer the eggs to the prepared pan. 

Set the pan inside a 9×13-inch baking dish. Carefully pour the boiling water into the 9×13-inch baking dish. Carefully transfer the pan to the oven. Set a sheet pan on top of the pan to cover. Cook for 25-35 minutes (or potentially longer), but start checking after 25 minutes. To check for doneness, remove the sheet pan, and gently touch the egg custard — it should feel set. If it is not set, recover the pan and set the timer for 5 minutes more. My eggs consistently cook in 25 to 30 minutes. 

Carefully remove the egg custard from the water bath and set it on a cooling rack. Let rest for 10 minutes before cutting. Cut into 6 rectangles. Proceed with the recipe or transfer the rectangles to a storage vessel and store in the fridge for up to 1 week. """

egg_squares = None 