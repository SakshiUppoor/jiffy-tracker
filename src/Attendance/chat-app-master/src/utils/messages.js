const generateMessage = (username , text)=>{
    return {
        username : username,
        text : text,
        createdAt : new Date().getTime()
    }
}

const generateLocation= (username ,locationlink)=>{
    return {
        username,
        locationlink ,
        createdAt :new Date().getTime()
    }

}

module.exports ={
    generateMessage,
    generateLocation
}