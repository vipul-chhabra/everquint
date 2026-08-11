const compute=()=>{
  /*Reset table style*/
  if(document.getElementsByTagName('head')[0].getElementsByTagName('style')[0]){
      document.getElementsByTagName('head')[0].getElementsByTagName('style')[0].innerHTML = "";
  }


  let inputArr = document.getElementById("data").value.split(",");
  const invalidChar = /\D/;
  let max = -1;
  for(let i=0;i<inputArr.length;i++){
      if(inputArr[i]==='' || invalidChar.test(inputArr[i])){
          alert("Incorrect input!");

          //Reset tables
          document.getElementsByClassName("inp-vis")[0].innerHTML = "";
          document.getElementsByClassName("output")[0].innerHTML = "";
          return;
      }
      inputArr[i] = Number(inputArr[i]);
      if(inputArr[i]>max) max=inputArr[i];
  }
  const outVis = waterCalculation(inputArr);

  document.getElementsByClassName("inp-vis")[0].innerHTML = renderInput(inputArr, outVis, max, "inp-vis");
  document.getElementsByClassName("output")[0].innerHTML = renderOutput(inputArr, outVis, max, "out-vis");
}

const keyHandler=(e)=>{
  if (e.key==='Enter' && e.target.value) {
      // pressed enter
      compute();
    }
}


const renderInput = (inpArr, newInpArr, max, className)=>{
  if(document.getElementsByTagName('head')[0].getElementsByTagName('style')[0]){
  style = document.getElementsByTagName('head')[0].getElementsByTagName('style')[0];
   }
   else{
      style = document.createElement('style');
      document.getElementsByTagName('head')[0].appendChild(style);
  }
  let inputTableStyle = "";

  for(let i=0;i<inpArr.length;i++){
    
    for(let j=1;j<=max+1;j++){
        
        if(inpArr[i]>0 && inpArr[i]>=j){
            inputTableStyle +=`.${className} tr:nth-child(${max-j+2}) td:nth-child(${i+1}) {background-color: yellow;}`;
        }
        else if(newInpArr[i]>0 && newInpArr[i] >= j - inpArr[i] ){
            inputTableStyle +=`.${className} tr:nth-child(${max-j+2}) td:nth-child(${i+1}) {background-color: DeepSkyBlue;}`;
        }
        else {
            inputTableStyle+=`.${className} tr:nth-child(${max-j+2}) td:nth-child(${i+1}) {background-color: white;}`;
        }      
    }
    
  }

  style.appendChild(document.createTextNode(inputTableStyle));
  return render(inpArr, max);
}

function render(arr, max) {
  let render = "<table>";
  max=max+1;
  for(let i=0;i<max;i++) {
      render += "<tr>";
      for(let j=0;j<arr.length;j++){
          render+="<td></td>";
      }
      render += "</tr>";
  }
  render += "</table>";
  return render;
}

const renderOutput=(inpArr, newInpArr, max, tableClassName)=>{
  style = document.getElementsByTagName('head')[0].getElementsByTagName('style')[0];
  let units = totalUnits(newInpArr);
  resultBlock = `<h3>Output: ${units} ${units<=1?"Unit":"Units"}</h3>
                  <div class=${tableClassName}>`;

  let inputTableStyle = "";
  
  for(let i=0;i<inpArr.length;i++){
    for(let j=1;j<=max+1;j++){
        
        if(inpArr[i]>0 && inpArr[i]>=j){
            inputTableStyle +=`.${tableClassName} tr:nth-child(${max-j+2}) td:nth-child(${i+1}) {background-color: white;}`;
        }
        else if(newInpArr[i]>0 && newInpArr[i] >= j - inpArr[i] ){
            inputTableStyle +=`.${tableClassName} tr:nth-child(${max-j+2}) td:nth-child(${i+1}) {background-color: DeepSkyBlue;}`;
        }
        else {
            inputTableStyle+=`.${tableClassName} tr:nth-child(${max-j+2}) td:nth-child(${i+1}) {background-color: white;}`;
        }      
    }
  }

  style.appendChild(document.createTextNode(inputTableStyle));
  return resultBlock + render(newInpArr, max) + "</div>";
}

function totalUnits(outVisArr) {
  return outVisArr.reduce((acc,ele)=>{
      if(ele==-1) return acc;
      return acc+ele;
  },0);
}

const waterCalculation=(inpArr)=> {
  let newInpArr = new Array(inpArr.length);
  let maxLeft = 0 ;
  let maxRight = 0 ; 
  let leftArr = 0 ; 
  let rightArr = inpArr.length -1 ;
  while(leftArr < rightArr) {
      let newInputTableStyle = '';  
      if(inpArr[leftArr] <= inpArr[rightArr]){
        maxLeft = Math.max(maxLeft, inpArr[leftArr]) ;
        let value  =  maxLeft - inpArr[leftArr];
        newInpArr[leftArr] = value ; 
        leftArr++ ;
      }else{
        maxRight = Math.max(maxRight, inpArr[rightArr]) ;
        let rightValue = maxRight - inpArr[rightArr];
        newInpArr[rightArr] = rightValue;
        rightArr-- ;
      }
  }  
  return newInpArr ;
}