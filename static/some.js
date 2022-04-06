document.addEventListener("visibilitychange", function(){
    document.title = document.visibilityState;
    console.log(  document.visibilityState)
});