var elements
var past_color
function highlightByID(id){
  if(typeof elements !== 'undefined'){
    highlightSpans(elements, past_color)
  }
  elements = document.getElementsByClassName(id)
  if(past_color !== elements[0].style.backgroundColor){
    past_color = elements[0].style.backgroundColor
    highlightSpans(elements, "yellow")
  }
  if(elements[0].style.backgroundColor !== "yellow"){
    highlightSpans(elements, "yellow")
  }
}
function highlightSpans(elements, color){
    for(var i=0; i<elements.length; i++){
      elements[i].style.backgroundColor = color;
    }
}