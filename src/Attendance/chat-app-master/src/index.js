const path=require("path");
const express= require("express");
const http=require("http")  //Core HTTP module 
const socketio=require("socket.io")
const Filter=require("bad-words")
const {generateMessage , generateLocation}=require("./utils/messages")
const {addUser ,removeUser , getUser, getUsersInRoom}= require("./utils/users")

const app=express();
const server = http.createServer(app) 
const io=socketio(server)  
//The above statement just refactored the way we set up expess.By default express does it for us 
//Also we did server.listen() instead of app.listen()
//The only reason we did this was to pass server to the socketio(server) function

app.use(express.static(path.join(__dirname,"../public")))


//NOTE:The emit functions for connection and disconnect are inbiult by the socket.io ,we dont need to call them
io.on("connection",(socket)=>{
    //Here the parameter socket contains all the information about the event
    console.log("New user connected!")

    socket.on("join", ({username , room}, callback)=>{

        const {error , user } = addUser({ id : socket.id , username , room })
        
        if(error){
            return callback(error)
        }

        socket.join(user.room)
  
        socket.emit("message",generateMessage("Admin","Welcome"))
        socket.broadcast.to(user.room).emit("message",generateMessage("Admin",`${username} has joined!`)) //Sends message to everyone except the user who has joined
        io.to(user.room).emit("roomData",{
            room : user.room,
            users : getUsersInRoom(user.room)
        })
        callback()
    })

    socket.on("message",(message,callback)=>{
        const user =getUser(socket.id)

        const filter =new Filter()

        if(filter.isProfane(message)){
            return callback("PLease maintain your language.Profanity is prohibited!")
        }

        io.to(user.room).emit("message",generateMessage(user.username,message))
        callback()
    })

    socket.on("sendLocation",(position,callback)=>{   
        const user =getUser(socket.id)

        io.to(user.room).emit("locationMessage",generateLocation(user.username,`https://google.com/maps?q=${position.latitude},${position.longitude})`))
        callback()
    })

    socket.on("disconnect",()=>{
        const user = removeUser(socket.id)

        if(user){
            io.to(user.room).emit("message",generateMessage("Admin",`${user.username} has left!`))
            io.to(user.room).emit("roomData", {
                room : user.room ,
                users : getUsersInRoom(user.room)
            })
        }

    })

})



const PORT =process.env.PORT || 3000;
server.listen(PORT,()=>{
    console.log("server is up on port " + PORT);
})



//socket.emit() --Emits it to the particular user
//io.emit()  --Emits it to all the users
//socket.broadcast.emit()  --Emits it to all users except the one generating it