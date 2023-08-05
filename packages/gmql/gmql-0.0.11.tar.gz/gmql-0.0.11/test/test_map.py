import gmql as gl
gl.set_remote_address("http://gmql.eu/gmql-rest/")
gl.login()
gl.set_mode("remote")
d1 = gl.load_from_remote("Example_Dataset_1", owner="public")
r = d1.materialize()
