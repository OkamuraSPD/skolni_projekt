from json_manager import JsonManager


js = JsonManager('static/data.json')
data = js.read_json()

js.update_by_pin("1", 55)
