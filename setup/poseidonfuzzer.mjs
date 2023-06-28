import wasm_tester from "../../../node_modules/circom_tester/wasm/tester.js";
import * as path from "path";

async function poseidon(inputField1, inputField2, inputCircomPath) {
  const circuit = await wasm_tester(
    path.join(inputCircomPath, "./tests/circuits/poseidon_test.circom"),
    {
      prime: "secq256k1"
    }
  );

  // Using the same inputs as test_poseidon in wasm.rs
  const input = {
    inputs: [
      inputField1,
      inputField2
    ]
  };

  const w = await circuit.calculateWitness(input, true);
  
  return w[1];
}

var inputField1 = process.argv[2];
var inputField2 = process.argv[3];
var inputCircomPath = process.argv[4];
var output = await poseidon(inputField1, inputField2, inputCircomPath);
var resp = String(output);
console.log(resp);
