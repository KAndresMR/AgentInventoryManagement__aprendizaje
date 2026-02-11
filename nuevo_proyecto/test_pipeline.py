from planner.inventory_planner import run_inventory_pipeline

with open("avena.jpeg", "rb") as f:
    img = f.read()

result = run_inventory_pipeline(img)
print(result)
