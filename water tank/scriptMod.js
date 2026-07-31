function compute() {
  /*Reset table style*/
  if (
    document.getElementsByTagName("head")[0].getElementsByTagName("style")[0]
  ) {
    document
      .getElementsByTagName("head")[0]
      .getElementsByTagName("style")[0].innerHTML = "";
  }

  let inputArr = document.getElementById("data").value.split(",");
  const invalidChar = /\D/;
  let max = -1;
  for (let i = 0; i < inputArr.length; i++) {
    if (inputArr[i] === "" || invalidChar.test(inputArr[i])) {
      alert("Incorrect input!");

      //Reset tables
      document.getElementsByClassName("inp-vis")[0].innerHTML = "";
      document.getElementsByClassName("output")[0].innerHTML = "";
      return;
    }
    inputArr[i] = Number(inputArr[i]);
    if (inputArr[i] > max) max = inputArr[i];
  }
  const outVis = outVisArr(inputArr, max);

  document.getElementsByClassName("inp-vis")[0].innerHTML = renderInput(
    outVis,
    max,
    "inp-vis"
  );
  document.getElementsByClassName("output")[0].innerHTML = renderOutput(
    outVis,
    max,
    "out-vis"
  );
}

function keyHandler(e) {
  if (e.key === "Enter" && e.target.value) {
    // pressed enter
    compute();
  }
}

function outVisArr(arr, max) {
  let result = [];
  for (let i = 0; i < arr.length; i++) {
    result.push(max - arr[i]);
  }

  return result;
}

function renderInput(outVisArr, max, className) {
  if (
    document.getElementsByTagName("head")[0].getElementsByTagName("style")[0]
  ) {
    style = document
      .getElementsByTagName("head")[0]
      .getElementsByTagName("style")[0];
  } else {
    style = document.createElement("style");
    document.getElementsByTagName("head")[0].appendChild(style);
  }

  let inputTableStyle = "",
    outVisArrCopy = [...outVisArr];

  for (let i = 2; i <= max + 1; i++) {
    for (let j = 1; j <= outVisArrCopy.length; j++) {
      if (outVisArrCopy[j - 1] > 0) {
        inputTableStyle += `.${className} tr:nth-child(${i}) td:nth-child(${j}) {background-color: DeepSkyBlue;}`;
        outVisArrCopy[j - 1] -= 1;
      } else {
        inputTableStyle += `.${className} tr:nth-child(${i}) td:nth-child(${j}) {background-color: yellow;}`;
      }
    }
  }

  style.appendChild(document.createTextNode(inputTableStyle));
  return render(outVisArr.length, max);
}

function render(noOfCol, max) {
  let render = "<table>";
  max = max + 1;
  for (let i = 0; i < max; i++) {
    render += "<tr>";
    for (let j = 0; j < noOfCol; j++) {
      render += "<td></td>";
    }
    render += "</tr>";
  }
  render += "</table>";
  return render;
}

function renderOutput(outVisArr, max, tableClassName) {
  style = document
    .getElementsByTagName("head")[0]
    .getElementsByTagName("style")[0];
  let units = totalUnits(outVisArr);
  resultBlock = `<h3>Output: ${units} ${units <= 1 ? "Unit" : "Units"}</h3>
                    <div class=${tableClassName}>`;

  let inputTableStyle = "",
    outVisArrCopy = [...outVisArr];
  for (let i = 2; i <= max + 1; i++) {
    for (let j = 1; j <= outVisArrCopy.length; j++) {
      if (outVisArrCopy[j - 1] > 0) {
        inputTableStyle += `.${tableClassName} tr:nth-child(${i}) td:nth-child(${j}) {background-color: DeepSkyBlue;}`;
        outVisArrCopy[j - 1] -= 1;
      } else {
        inputTableStyle += `.${tableClassName} tr:nth-child(${i}) td:nth-child(${j}) {background-color: white;}`;
      }
    }
  }

  style.appendChild(document.createTextNode(inputTableStyle));
  return resultBlock + render(outVisArr.length, max) + "</div>";
}

function totalUnits(outVisArr) {
  return outVisArr.reduce((acc, ele) => {
    if (ele == -1) return acc;
    return acc + ele;
  }, 0);
}