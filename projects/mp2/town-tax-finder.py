"""Mini Project 2.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import requests

    return (requests,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 2
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    *Who would use this, and what decision does it help them make? Two or three sentences, in words somebody outside this course would understand.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This tool could help anyone looking to buy a home or move to a new area. It allows people to compare average home prices and property taxes across different towns, helping them find affordable places to live in and make better financial decisions depending on their economic conditions.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My plan before AI

    Before you ask your agent anything, open the API's address in your browser and read what comes back. Then write how you would solve it: the steps, in order, in plain words, in five lines or more. Then answer these:

    Which functions will your tool need? For each, what goes in and what comes out?
    Which addresses will they request?
    How will you know you have every record?
    Which check will you use in section 6, and which two numbers should agree?


    Commit with the message mp2: plan before AI.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First, I would use the API to get a list of all towns in Middlesex County. With that data, I would first check the total number of towns and make sure I collected all of them. Next, I would get tax information for each town. I would also look for the average value and average yearly tax bill for each town. To find only the ones we are looking for, I would keep only towns with average home values of $700,000 or less and tax bills under $8,000. With that, I would sort the remaining towns from the lowest to the highest tax bill. Finally, I would display the results in a table so the couple can compare their options.

    Plainly, I would need to use loops and dictionaries to record the information requested. First, a function which extracts all towns within a county. Second, take town codes and a specific year to return town property tax information for that year. Third, with the conditions/limits requested find affordable towns and return a list of towns who satisfy the given requests.

    I would use the following addresses since they contain the information we are looking for: /ma/towns/{dor_code}/history" and "/ma/county=Middlesex".

    To ensure I have each record, I would check the total number of towns reported by the API in pagination. Then, I would count the towns I collected from all pages. Both numbers should be equal to ensure I have all towns in the county.

    For section 6, I plan on checking my calculated bill to the average bill reported by the API. The two numbers should be approximately equal.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    *Every input in one cell.*
    """)
    return


@app.cell
def _():
    county = "Middlesex"
    budget_dollars = 700000
    tax_limit_dollars = 8000
    fiscal_year = 2026
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    *Your functions, and the code that uses them.*
    """)
    return


@app.cell
def _(requests):
    # get all towns from a county

    def get_towns(county): #will search for towns in a county
        all_towns = [] #create an empty town list
        page = 1 

        while True: # start a loop in which we repeat the following code until Python is told otherwise
            reply = requests.get( #request information from API
                "https://oim.zhili.dev/ma/towns",
                params={
                    "county": county,
                    "page": page,
                    "per_page": 100
                }
            )

            data = reply.json() #convert information extracted from API into a dictionary
            towns = data["items"]
            total = data["pagination"]["total"] #store total number of towns in "total"

            all_towns.extend(towns) #add all towns to list

            if len(all_towns) >= total: #once we collect all towns the loop stops
                break

            page += 1 #and the function is free to move to the next page

        return all_towns 

    return (get_towns,)


@app.cell
def _(requests):
    #get tax information for each town

    def town_history(dor_code, year): #create a function that takes a town's unique code and the fiscal year we want to dig further in
        reply = requests.get( #request infromaiton from API
            f"https://oim.zhili.dev/ma/towns/{dor_code}/history",
            params={"fiscal_year": year}
        )

        history = reply.json()

        for record in history["years"]: #look for information from a specific year
            if record["fiscal_year"] == year:
                return record

        return None #if this year is not found, then return "None"

    return (town_history,)


@app.cell
def _(town_history):
    #testing
    wellesley = town_history("317", 2026)

    wellesley
    return


@app.cell
def _(get_towns, town_history):
    #find the towns that meet budget
    #average home costs $700,000 or less AND the annual property tax bill is under $8,000.

    def find_affordable_towns(county, budget, tax_limit, year): #create fucniton with these 4 inputs
        towns = get_towns(county) #get all towns
        affordable = []

        for town in towns: #this loop looks at each towns' information
            name = town["name"]
            code = town["dor_code"]

            history = town_history(code, year)

            if history is not None: #makes sure we get the information solely for this year
                value = history["average_single_family_value_dollars"] #we get only the information we need/want
                rate = history["residential_rate_per_thousand"]
                bill = history["average_single_family_bill_dollars"]

                if value <= budget and bill < tax_limit: #apply conditions 
                    affordable.append({ #we use append to add a dictionary containing the information for each qualifying town
                        "Town": name,
                        "Average Home Value": value,
                        "Residential Tax Rate": rate,
                        "Average Tax Bill": bill
                    })

        affordable.sort(key=lambda x: x["Average Tax Bill"]) #use average tax bill to sort from lowest to highest

        return affordable #return qualifying towns

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Your answer

    *Your result table, printed with print and f-strings with the columns lined up, and one sentence that answers the question in section 1 with the numbers in it. Print the sentence from code with an f-string, so that it changes when the data does.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How do I know these numbers are right?

    *Reach at least one result a second way, in this notebook, and show that the two agree. Write a cell that gets the same number from other fields, or open the raw reply in your browser and find each number of one row of your table there. For instance: an average bill is close to the average value times the tax rate divided by 1,000; an order's total equals the sum of its lines; the number of records you collected equals the total the API reports. At least one of those checks runs as code, and shows both numbers.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working with an Agent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell. If the agent got it right the first time: What did you do to verify that?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Reading it back.

    *Pick two functions in your notebook that your agent wrote or helped write. For each, write in your own words what goes in, what comes out, and one line you had to ask about. Then choose one change to what the tool does, such as another county, another week or another rule, and write what you expect to change in the answer. Commit with the message mp2: prediction, make the change, run it, and write what happened and whether it matched.*
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Going Further

    *What you tried past the main task, what you found, and where it is in the notebook.*
    """)
    return


if __name__ == "__main__":
    app.run()
