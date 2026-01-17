html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>HOROLOGY.IA</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script></head>
<body><h1>Test</h1>anvas id="test"></canvas>
<script>new Chart(document.getElementById("test"),{type:"bar",data:{labels:["A","B"],datasets:[{data:[10,20]}]}})</script>
</body></html>"""
with open("index_new.html","w") as f:
    f.write(html)
