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
    return county, fiscal_year


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

    return (find_affordable_towns,)


@app.cell
def _(find_affordable_towns):
    #test
    affordable_towns = find_affordable_towns(
        "Middlesex", 700000, 8000, 2026
    )

    affordable_towns
    return (affordable_towns,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Your answer

    *Your result table, printed with print and f-strings with the columns lined up, and one sentence that answers the question in section 1 with the numbers in it. Print the sentence from code with an f-string, so that it changes when the data does.*
    """)
    return


@app.cell
def _(affordable_towns):
    print(f"{'Town':<20} {'Home Value':>15} {'Tax Rate':>12} {'Tax Bill':>15}")
    print("-" * 65)

    for town in affordable_towns:
        print(f"{town['Town']:<20} ${town['Average Home Value']:>14,.0f} {town['Residential Tax Rate']:>12.2f} ${town['Average Tax Bill']:>14,.0f}")
    return


@app.cell
def _(affordable_towns, county, fiscal_year):
    if len(affordable_towns) > 0:
        best = affordable_towns[0]

        print(
            f"For {fiscal_year}, {best['Town']} is the most affordable qualifying town "
            f"in {county} County based on property taxes, with an average home value of "
            f"${best['Average Home Value']:,.0f} and an annual property tax bill of "
            f"${best['Average Tax Bill']:,.0f}."
        )
    else:
        print(f"No towns in {county} County meet both budget and tax limits.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How do I know these numbers are right?

    *Reach at least one result a second way, in this notebook, and show that the two agree. Write a cell that gets the same number from other fields, or open the raw reply in your browser and find each number of one row of your table there. For instance: an average bill is close to the average value times the tax rate divided by 1,000; an order's total equals the sum of its lines; the number of records you collected equals the total the API reports. At least one of those checks runs as code, and shows both numbers.*
    """)
    return


@app.cell
def _(town_history):
    wellesley_data = town_history("317", 2026)

    wellesley_value = wellesley_data["average_single_family_value_dollars"]
    wellesley_rate = wellesley_data["residential_rate_per_thousand"]
    wellesley_bill = wellesley_data["average_single_family_bill_dollars"]

    wellesley_calculated = wellesley_value * wellesley_rate / 1000

    print("Town: Wellesley")
    print(f"API Tax Bill: ${wellesley_bill:,.2f}")
    print(f"Calculated Tax Bill: ${wellesley_calculated:,.2f}")

    if abs(wellesley_bill - wellesley_calculated) < 5:
        print("The two numbers agree!")
    else:
        print("The two numbers do not agree.")

    #this cell looks at Wellesley and compares to a cell I ran above when checking if my functions were working.
    return


@app.cell
def _(affordable_towns):
    check_town = affordable_towns[0]

    check_value = check_town["Average Home Value"]
    check_rate = check_town["Residential Tax Rate"]
    check_bill = check_town["Average Tax Bill"]

    calculated_bill = check_value * check_rate / 1000

    print(f"Town: {check_town['Town']}")
    print(f"API Tax Bill: ${check_bill:,.2f}")
    print(f"Calculated Tax Bill: ${calculated_bill:,.2f}")

    if abs(check_bill - calculated_bill) < 5:
        print("The two numbers agree!")
    else:
        print("The two numbers do not agree.")

    #this one looks at our affordable towns list, one we care about
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


@app.cell
def _():
    #mo.ui.table(affordable_towns)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    My agent gave me this code to print out the table above. I did not take it as it recommended as it was not the kind of table we were looking for. The assignment asked to print a results table with f-strings in a traditional manner. Although this idea from my agent was interactive and a good possible option, it was more complex and not what the assignment required, so I chose not to use it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Reading it back.

    *Pick two functions in your notebook that your agent wrote or helped write. For each, write in your own words what goes in, what comes out, and one line you had to ask about. Then choose one change to what the tool does, such as another county, another week or another rule, and write what you expect to change in the answer. Commit with the message mp2: prediction, make the change, run it, and write what happened and whether it matched.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Function 1: get_towns(county)

    The purpose of this function is to take the name of a county and return a list of all the towns in that county. One part I needed help understanding was:

    "data = reply.json()
    towns = data["items"]
    total = data["pagination"]["total"]"

    I learned that `reply.json()` converts the API response into Python data we can use and data["pagination"]["total"] tells us how many towns there are in total. In which pagination aims to keep track of how many towns exist across all pages of results, since the API might not return every town in a single response.


    --


    Function 2: find_affordable_towns(county, budget, tax_limit, year)

    This function takes the county, budget, tax limit, and year as inputs. It returns a list of towns that meet both the home price and property tax limits, sorted from the lowest to highest tax bill.

    One line I needed help understanding was:

    "affordable.sort(key=lambda x: x["Average Tax Bill"])"

    I learned that .sort() organizes the list, but more specifically that "lambda" tells Python to use the average tax bill to sort the towns from cheapest to most expensive.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Prediction:**

    I predict that changing from Middlesex County to Norfolk County will result in fewer towns meeting both conditions: the $700,000 home budget and the $8,000 annual tax limit. I also expect that the town with the lowest property tax bill in Norfolk will have a higher average tax bill than the cheapest qualifying town in Middlesex. I want to see whether changing counties makes it harder to find an affordable property, even when the budget stays the same.
    """)
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
