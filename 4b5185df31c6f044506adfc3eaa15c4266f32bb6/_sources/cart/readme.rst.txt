.. _cart_readme:

=====================
NgChat Cart Overview
=====================
A set of python classes and methods that provide cart functionality for chat bots.

.. contents:: Table of Contents
    :local:
    :depth: 3

Purpose
--------
We believe that chat and voice based e-commerce through conversational AI has a lot potential. However, when using Rasa to build a bot for ordering food and drink, we found the custom actions too restrictive. Our solution is to provide a generalized cart implementation that be integrated into any chat bot. cart.py includes classes for the cart and menu, as well as classes for items and options. Callable methods cover a wide range of capabilities, including but not limited to:
    - Loading and setting a menu
    - Describing menu categories/items
    - Querying the menu for item matches or suggestions
    - Customizing an item
    - Adding/removing items from the cart
    - Caching user carts for multi-user support

Implementation
---------------
The main class is the ``Cart`` class, and most methods can be accessed through this class. A menu must be loaded before the cart can be modified or accessed. View the technical documentation :ref:`here<ngchat_cart>` for implementation details.


Integration with Rasa
----------------------
Custom actions are required to bridge the gap between Rasa and the cart. Use the custom actions to collect information from the tracker, perform checks, and dispatch utterances; call ``cart.py`` methods from a custom action to manipulate the cart, menu, or items. 

Training Data Generation
-------------------------
ngChat Cart provides methods to automatically produce Chatette entity examples and Rasa lookup tables. Chatette templates are used to generate initial training data for bots based on the expansion of templates marked up with entities and intents. The ngChat Cart includes a method to extract menu-specific entities into a chatette template, which can then be included in a bot's Chatette templates to easily add menu-specific entity data to your Chatette templates. These are intended to be used with the ``cart.chatette`` template file, which includes templates for the intents and entities used by ngChat Cart. 

Similarly, the ngChat Cart supports automatic lookup table generation from a menu. Rasa bots can incorporate lookup tables to ensure that specific strings are consistently identified as entities. This method will output separate lookup table files for each relevant entity. These lookup tables must then be referenced in a NLU md file.

There are convenience scripts provided to call these methods. The scripts will generate lookup tables or chatette aliases for ``options``, ``items``, and ``query_topics``. For detailed instructions on how to run these scripts, see the :ref:`tutorial<cart_tutorial>`.


CART MENU FORMAT
-----------------
ngChat Cart uses a standardized menu format which is designed to be compatible with the majority of e-commerce products. The menu is composed of different objects: the top level ``menu`` object, ``products``, ``modifiers``, ``modifier_groups``, and ``variants``.

Menu
-----
At the top level, A menu is composed of 4 attributes: ``name``, ``currency``, ``products``, ``modifiers``.

.. code-block::

    {
        "store_name": "Text",
        "currency": "Text",
        "products": "List[Dict[Text, Any]]",
        "modifiers": "List[Dict[Text, Any]]"
    }

The ``store_name`` is the way that the name will be displayed to users of the bot. 

The ``currency`` field is the three-letter acronym for the currency used to represent prices in the menu: 

.. code-block::

    "currency: "USD"

The products and modifiers fields are both lists of dictionary objects. The ``product`` list contains information about purchasable items and combos (Caffe Americano, 8 Piece Family Meal, Grande Nacho Box Combo, etc). The ``modifiers`` list contains information about modifiers that can be attached to these products. 

Product
--------
Products are purchasable items on the menu. 
A product entry has the following format:

.. code-block::

    {
        "name": Text,  # The item's name (ex/ Americano, Cheeseburger Meal)
        "id": Text,  # A unique identifier for the product
        "aliases": List[Text],  # A list of synonyms for this item, e.g., ["number 7", "5 dollar fill up"].
        "categories": List[Text],  # A list of category names relevant to the product (ex/ Hot Drinks)
        "type": {'combo', 'item', 'virtual'},  # product type, as explained above
        "subtype": Optional[Text] # None or more specific types, such as "sides", "beverages"
        "recommendation_score": int,  # A base recommendation score, used for suggesting items to users
        "tags": List[Text],  # A list of tags (ex/ hot, sweet, drink, coffee) used for item retrieval
        "description": Optional[Text],  # A description of the product
        "ingredients": List[Text],  # A list of ingredients in the product
        "calories": Optional[Union[int, List[int]]],  # calorie information. Can be represented as an int, or a range [int, int]
        "price": float,  #  base item price (without modifiers)
        "image": Optional[Text],  # a url to an image
        "modifier_groups": List[Dict[Text, Any]]  # A list of modifier groups (customizable options)
    }

There are three types of products: ``item``, ``combo``, and ``virtual``.

**Item**

A product of type ``item`` is a single purchasable item. These items can be customized with modifiers only in their modifier groups. Here's an example of an item from the Starbucks menu:

.. code-block:: JSON

    {
        "name": "Caffè Americano",
        "id": 776000,
        "aliases": [
            "cafe americano",
            "coffee americano"
        ]
        "categories": [
            "Hot Coffees"
        ],
        "type": "item",
        "recommendation_score": 538000,
        "tags": [
            "Hot",
            "beverages"
        ],
        "description": "Espresso shots topped with hot water create a light layer of crema culminating in this wonderfully rich cup with depth and nuance. \n Pro Tip: For an additional boost, ask your barista to try this with an extra shot.",
        "ingredients": [
            "Water",
            "Brewed Espresso"
        ],
        "calories": 15,
        "price": 2.95,
        "image": "https://globalassets.starbucks.com/assets/f12bc8af498d45ed92c5d6f1dac64062.jpg",
        "modifier_groups": [
            {
                "name": "size",
                "category": "Sizes",
                "query_users_for_modifier": true,
                "minimum": 1,
                "maximum": 1,
                "modifiers": [
                    {
                        "name": "Short",
                        "id": 663000,
                        "default": false,
                        "price_change": -0.7,
                        "calorie_change": -10
                    },
                    {
                        "name": "Tall",
                        "id": 663001,
                        "default": false,
                        "price_change": -0.5,
                        "calorie_change": -5
                    },
                    {
                        "name": "Grande",
                        "id": 663002,
                        "default": true,
                        "price_change": 0.0,
                        "calorie_change": 0
                    }
                ]
            }
        ]
    }


**Combo**

A ``combo`` product is a set of items that come together; for example, a cheesebuger meal that comes with a drink and fries. In contrast to an ``item`` type, a combo can have modifiers, as well as other items in it's modifier groups. In the case of a combo, you may be able to choose between several items (do you want a cheeseburger, hambuger, or veggieburger?), and each item may also be customized by its own modifiers. The crucial difference between an item and combo is that a combo will have items in it's modifier groups, and then will check if those items have customizable options. A simple item type will never check if it's modifiers have further customizations. Here's an example of a combo from the TacoBell menu:

.. code-block:: JSON

    {
        "name": "Mexican Pizza Combo",
        "categories": [
            "Combos"
        ],
        "recommendation_score": 0,
        "type": "combo",
        "image": "https://www.tacobell.com/images/22604_4._mexican_pizza_combo_640x650.jpg",
        "description": "Served with a large taco, 2 crunchy taco supreme and a Mexican pizza.",
        "tags": [
            "Combos"
        ],
        "calories": [
            1330,
            1330
        ],
        "price": 7.19,
        "id": "22604",
        "modifier_groups": [
            {
                "name": "Item 1: Select your drink",
                "minimum": 1,
                "maximum": 1,
                "modifiers": [
                    {
                        "name": "Mountain Dew Baja Blast® Freeze - Regular",
                        "id": "1491",
                        "default": false,
                        "price_change": 0.5
                    },
                    {
                        "name": "Strawberry Skittles® Freeze - Regular",
                        "id": "1615",
                        "default": false,
                        "price_change": 0.4
                    }
                ]
            },
            {
                "name": "Item 3: Crunchy Taco Supreme®. Would you like to swap this for something else?",
                "minimum": 0,
                "maximum": 1,
                "modifiers": [
                    {
                        "name": "Soft Taco Supreme®",
                        "id": "22111",
                        "default": false,
                        "price_change": 0.0
                    },
                    {
                        "name": "Crunchy Taco Supreme®",
                        "id": "22101",
                        "default": true,
                        "price_change": 0.0
                    },
                    {
                        "name": "Nacho Cheese Doritos® Locos Tacos Supreme®",
                        "id": "22173",
                        "default": false,
                        "price_change": 0.6
                    }
                ]
            }
        ]
    }

**Virtual**

A ``virtual`` product is similar to a combo, but always contains an item in its modifier_group whose details and own modifier groups the bot should treat as if they were those of the main item. For example, rather than selecting a Breakfast Burrito, then choosing between bacon and sausage as addons, a user would select the virtual Breakfast Burrito, then select either "Breakfast Burrito - Bacon" or "Breakfast Burrito - Sausage" as a modifier. The bot should then treat this selection as it were the actual cart item when displaying information. Here's an example of a virtual item from the TacoBell menu:

.. code-block:: JSON

    {
        "name": "Power Menu Bowl",
        "categories": [
            "Specialties",
            "Power Menu"
        ],
        "recommendation_score": 0,
        "type": "virtual",
        "image": "https://www.tacobell.com/images/22488_power_menu_bowl_640x650.jpg",
        "description": "We start with a bed of seasoned rice and top it with fire grilled chicken, black beans, fresh pico de gallo, premium guacamole, sour cream, lettuce, shredded cheddar cheese and avocado ranch sauce.",
        "tags": [
            "Specialties",
            "Power Menu"
        ],
        "calories": [
            470
        ],
        "price": 5.49,
        "id": "virtual-22488",
        "modifier_groups": [
            {
                "name": "Which style of Power Menu Bowl would you like?",
                "minimum": 1,
                "maximum": 1,
                "modifiers": [
                    {
                        "name": "Power Menu Bowl - Chicken",
                        "id": "22488",
                        "default": true
                    },
                    {
                        "name": "Power Menu Bowl - Steak",
                        "id": "22489",
                        "default": false
                    }
                ]
            }
        ]
    }

And here's the entry for the ``Power Menu Bowl - Chicken``:

.. code-block:: JSON

    {
        "name": "Power Menu Bowl - Chicken",
        "categories": [],
        "recommendation_score": 0,
        "type": "item",
        "image": "https://www.tacobell.com/images/22488_power_menu_bowl_640x650.jpg",
        "description": "We start with a bed of seasoned rice and top it with fire grilled chicken, black beans, fresh pico de gallo, premium guacamole, sour cream, lettuce, shredded cheddar cheese and avocado ranch sauce.",
        "tags": [],
        "calories": [
            45
        ],
        "price": 5.49,
        "id": "22488",
        "modifier_groups": [
            {
                "name": "Would you like to change the protein?",
                "minimum": 0,
                "maximum": 1,
                "modifiers": [
                    {
                        "name": "No Chicken",
                        "id": "2271",
                        "default": false,
                        "price_change": 0.0
                    },
                    {
                        "name": "Extra Chicken",
                        "id": "2273",
                        "default": false,
                        "price_change": 1.3
                    },
                    {
                        "name": "Shredded Chicken",
                        "id": "22782",
                        "default": false,
                        "price_change": 0.0
                    }
                ]
            }
        ]
    }

Note that the two items in its modifier groups in turn have their own distinct modifier groups. The virtual item lets us take advantage of a system already in place for combos (i.e. listing items in modifier groups) in order to set up this kind of conditionality of modifier groups without adding additional complexity. That is, it gives us an easy way to say "if you get it with chicken, here are the modifier groups for that, but if you get it with steak, here are the modifier groups for that."


Modifier groups
----------------
Each product has a list of ``modifier_groups`` which contain possible customizations/modifiers for the product. Modifier groups organize these modifiers into meaningful groups which have information about the group type, min and max number of selections, and whether or not the bot should ask the user about the group. Here's the format for a modifier group:

.. code-block::

    "name": Text,  # The name of the group (ex/ size, sauces)
    "category": Text,  # A more general category for the group (ex/ toppings, sides)
    "query_users_for_modifier": bool,  # whether the bot should ask the user about the group
    "minimum": int,  # minimum number of modifier selections from the group
    "maximum": int,  # maximum number of modifier selections from the group (-1 = no limit)
    "modifiers": List[Dict[Text, Any]]  # A list of possible modifiers

Modifiers
----------
The ``modifier`` is the actual customization that can be applied to the product. For example: ``small``, ``sour cream``, or ``caramel drizzle``. Modifiers exist in two places in the menu: inside a product's modifier group, and inside the modifiers list of the menu. Modifier objects in the modifier list are the absolute representation of the modifier; they contain the concrete information about the modifier that is true no matter what item it is attached to. Here is the format for a full modifier:

.. code-block::

    {
        "name": Text,  # modifier name (ex/ caramel drizzle, sour cream)
        "id": Text,  # a unique id for the modifier
        "type": "modifier",  # specify this object is type modifier
        "countable": bool,  # whether this modifier is countable or not (# of shots vs size Tall)
        "quantity": Optional[int],  # The default quantity, if it is countable
        "unit_of_measure": Text,  # how the quantity is measured (ex/ shots, pumps, packets)
        "price": float,  # price, if the modifier has a standard price
        "calories": Optional[Union[int, List]],  # calories, if the modifier has standard calories
        "description": Optional[Text],  # optional description
        "image": Optional[Text],  # url if there is an image available
        "variants": Dict[Text, [Dict[Text, Any]]]  # A list of modifier variants
    }

Modifiers inside a product's modifier group contain information about how the modifier is when it is attached to a specific item. The information in these modifiers can be thought of as overrides - in general all the information about a modifier can be found in the menu modifiers list, but sometimes the price or calories of a modifier changes depending on what item it is modifying. Here's the format for a modifier inside a modifier group:

.. code-block::

    "name": Text,  # The name of the modifier for easy access
    "id": int,  # the if of the modifier (refers back to the modifier object in the menu modifier list)
    "default": bool,  # if this modifier comes with the item by default or not
    "price_change": Optional[float],  # how much this option will change the base price of the item
    "calorie_change": Optional[Union[int, list[int, int]],  # how much this option will change the base calories
    "variants": List[Dict[Text, Any]]  # A list of modifier variants

Variants
---------
``variants`` are slightly different versions of a modifier. For example, if there is a modifier ``whipped cream``, it might have the variants ``extra whipped cream``, ``light whipped cream``, and ``no whipped cream``. By definition these variants contradict each other, and therefor only one variant from a single modifier can be added to an item. Similar to how modifiers can override certain aspects of an item, variants can override certain attributes of their parent modifier, such as price and calories. All the possible variants for a modifier can be found in the menu's ``modifiers`` list. If a specific item can have a variant as a modifier, that variant will appear in the variants list of the modifier in the modifier group.  Here is the format for variants:

.. code-block::

    "name": Text,  # The name of the variant
    "price_change": Optional[float],  # how this modification will affect the price of the product
    "calorie_change": Optional[Union[int, list[int, int]]],  # how this modification will affect the calories of the product

JSON Menu Format Schema Overview
---------------------------------
menu file naming: '/{store_name}.json'

.. code-block::

    {
        "store_name": Text,
        "currency": Text,
        "products": [
            {
                "name": Text,
                "id": Text,
                "categories": [Text],
                "type": {'item', 'combo', 'virtual'}
                "recommendation_score": int,
                "tags": [Text],
                "description": Text,
                "ingredients": [Text],
                "calories": {int, [int, int]},
                "price": float,
                "image": Text,
                "modifier_groups": [
                    {
                        "name": Text,
                        "category": Text,
                        "query_user_for_modifier": bool,
                        "minimum": int,
                        "maximum": int,
                        "modifiers": [
                            {
                                "name": Text,
                                "id": Text,
                                "price_change": float,
                                "calorie_change": int,
                                "variants": [
                                    {
                                        "name": Text,
                                        "price_change": float,
                                        "calorie_change": int
                                    }, ...
                                ]
                            }, ...
                        ]
                    }, ...
                ]
            }, ...
        ],
        "modifiers": [
            {
                "name": Text,
                "id": Text,
                "type": "modifier",
                "countable": bool,
                "quantity": int,
                "unit_of_measure": Text,
                "price": float,
                "calories": int,
                "description": Text,
                "image": Text,
                "variants": [
                    {
                        "name": Text,
                        "price_change": float,
                        "calorie_change": int
                    }, ...
                ]
            }, ...
        ]
    }

.. NOTE:: Base price should be based on the default version of the item, like the standard size. Base price is summed with the price of the item's modifiers to get the total cost.