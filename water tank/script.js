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
  const outVis = outVisArr(inputArr);

  document.getElementsByClassName("inp-vis")[0].innerHTML = renderInput(inputArr,outVis, max, "inp-vis");
  document.getElementsByClassName("output")[0].innerHTML = renderOutput(outVis, max, "out-vis");
}

const keyHandler=(e)=>{
  if (e.key==='Enter' && e.target.value) {
      // pressed enter
      compute();
    }
}

const outVisArr=(arr)=>{
  let result=[];
  let lastValueForForwardCase=0;
  let lastValueForBackwardCase=0;
  for (let fc = 0; fc < arr.length; fc++) {
      let element = arr[fc];
      if (element == 0) {
          result.push(lastValueForForwardCase);
      }else{
          result.push(-1);
          lastValueForForwardCase=element;
      }
  }
  for (let  bc = arr.length - 1; bc >= 0; bc--) {
      let element = arr[bc];
      if (element == 0) {
          result[bc] = result[bc] - lastValueForBackwardCase > 0 ? lastValueForBackwardCase : result[bc];
      }else{
          lastValueForBackwardCase=element;
      }
  }

  return result;
  
}

const renderInput = (inpArr, outVisArr, max, className)=>{
  if(document.getElementsByTagName('head')[0].getElementsByTagName('style')[0]){
  style = document.getElementsByTagName('head')[0].getElementsByTagName('style')[0];
   }
   else{
      style = document.createElement('style');
      document.getElementsByTagName('head')[0].appendChild(style);
  }

  let inputTableStyle = "";
  for(let i=0;i<outVisArr.length;i++) {
      if(outVisArr[i]!=0 && outVisArr[i]!=-1){
          inputTableStyle+=`.${className} td:nth-child(${i+1}) {background-color: DeepSkyBlue;}`;
          for(let j=1;j<=max-outVisArr[i]+1;j++) {
              inputTableStyle+=`.${className} tr:nth-child(${j}) td:nth-child(${i+1}) {background-color: white;}`;
          }
      }
      if(outVisArr[i]==-1) {
          inputTableStyle+=`.${className} td:nth-child(${i+1}) {background-color: yellow;}`;
          for(let j=1;j<=max-inpArr[i]+1;j++) {
              inputTableStyle+=`.${className} tr:nth-child(${j}) td:nth-child(${i+1}) {background-color: white;}`;
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

const renderOutput=(outVisArr, max, tableClassName)=>{
  style = document.getElementsByTagName('head')[0].getElementsByTagName('style')[0];
  let units = totalUnits(outVisArr);
  resultBlock = `<h3>Output: ${units} ${units<=1?"Unit":"Units"}</h3>
                  <div class=${tableClassName}>`;

  let inputTableStyle = "";
  for(let i=0;i<outVisArr.length;i++) {
      if(outVisArr[i]!=0 && outVisArr[i]!=-1){
          inputTableStyle+=`.${tableClassName} td:nth-child(${i+1}) {background-color: DeepSkyBlue;}`;
          for(let j=1;j<=max-outVisArr[i]+1;j++) {
              inputTableStyle+=`.${tableClassName} tr:nth-child(${j}) td:nth-child(${i+1}) {background-color: white;}`;
          }
      }
  }

  style.appendChild(document.createTextNode(inputTableStyle));
  return resultBlock + render(outVisArr, max) + "</div>";
}

function totalUnits(outVisArr) {
  return outVisArr.reduce((acc,ele)=>{
      if(ele==-1) return acc;
      return acc+ele;
  },0);
}