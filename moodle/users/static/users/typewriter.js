const TypeWriter= function(txtElement, words , wait=3000){
    this.txtElement=txtElement;
    this.words=words;
    this.txt='';
    this.wordIndex=0;
    this.wait=parseInt(wait,10);
    this.type();
    this.isDeleting=false;


}

//Type Menthod
TypeWriter.prototype.type=function(){
    
    // current index of the word
    const current=this.wordIndex%this.words.length;
    // get full text of the current word
    const fullTxt=this.words[current];

    // check if deleting
    if (this.isDeleting){
        // remove a char
        this.txt=fullTxt.substring(0,this.txt.length-1);
    }

    else{
        // add a char
        this.txt=fullTxt.substring(0,this.txt.length+1);

    }

    //Insert txt into element
    this.txtElement.innerHTML=`<span class="txt">${this.txt}</span>`;

    //Typespeed
    let typeSpeed=300;

    if (this.isDeleting){
        typeSpeed/=2;
    }
    
    // If word is complete
    if (!this.isDeleting&&this.txt===fullTxt){
        //Make a pause at the end
        typeSpeed=this.wait;
        // set delete to true
        this.isDeleting=true;
    }
    else if (this.isDeleting&&this.txt===""){
        this.isDeleting=false;

        // Move to next word;
        this.wordIndex++;

        //Pause before start typing again
        typeSpeed=500;
    }


    //if not 


    setTimeout(()=>this.type(),typeSpeed)
}

// DOM on load
document.addEventListener('DOMContentLoaded', init);

// Init App
function init(){
    const txtElement=document.querySelector('.txt-type');
    const words=JSON.parse(txtElement.getAttribute("data-words"));
    const wait=txtElement.getAttribute('data-wait');

    new TypeWriter(txtElement,words, wait);

}