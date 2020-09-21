"""
Global Config File

"""

units_pattern = ["thousands","millions"] #acceptable units
company_names_pattern = [".*Inc\.",".*CORPORATION",".*International",".*Subsidiaries",".*Incorporation"] #acceptable company names

# statements to consider
statements = [
".*Consolidated.*Statement.*Operations.*",
".*Consolidated.*Statement.*Income.*",
".*Consolidated.*Statement.*Earnings.*",
]

total_revenue = [
"Total Net Revenue","Total Revenues","Total Revenue","Net Sale","Revenues","Revenue","Net Revenues","Net Revenue","Net Sales","Net Revenue"
]

sga_patterns = ["General.*administrative.*","Selling.*informational.*administrative.*","Selling.*general.*administrative","Total.*selling.*administrative.*","Marketing.*administration.*research.*"
]

cost_of_goods_sold =["Total costs and expenses","Total cost of revenues","Cost of Sale.*","COGs","Cost of goods sold","Cost of Revenue.?"]


