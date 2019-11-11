const path = require("path");
const express = require("express");
const http = require("http"); //Core HTTP module
const socketio = require("socket.io");
const Filter = require("bad-words");
const app = express();
const server = http.createServer(app);
const io = socketio(server);

app.set("view-engine", "ejs");

app.get("/", (req, res) => {
  res.render("index.ejs", { name: "Sakshi" });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log("server is up on port " + PORT);
});
