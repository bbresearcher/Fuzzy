mod k256_consts;
pub mod poseidon_k256;
//use k256::FieldBytes;
use ff::PrimeField;
use std::env;

pub struct PoseidonConstants<F: PrimeField> {
    pub round_keys: Vec<F>,
    pub mds_matrix: Vec<Vec<F>>,
    pub num_full_rounds: usize,
    pub num_partial_rounds: usize,
}

impl<F: PrimeField> PoseidonConstants<F> {
    pub fn new(
        round_constants: Vec<F>,
        mds_matrix: Vec<Vec<F>>,
        num_full_rounds: usize,
        num_partial_rounds: usize,
    ) -> Self {
        Self {
            num_full_rounds,
            num_partial_rounds,
            mds_matrix,
            round_keys: round_constants,
        }
    }
}

pub struct Poseidon<F: PrimeField> {
    pub state: [F; 3],
    pub constants: PoseidonConstants<F>,
    pub pos: usize,
}

impl<F: PrimeField> Poseidon<F> {
    pub fn new(constants: PoseidonConstants<F>) -> Self {
        let state = [F::zero(); 3];
        Self {
            state,
            constants,
            pos: 0,
        }
    }

    pub fn hash(&mut self, input: &[F; 2]) -> F {
        // add the domain tag
        let domain_tag = F::from(3); // 2^arity - 1
        let input = [domain_tag, input[0], input[1]];

        self.state = input;

        let full_rounds_half = self.constants.num_full_rounds / 2;

        // First half of full rounds
        for _ in 0..full_rounds_half {
            self.full_round();
        }

        // Partial rounds
        for _ in 0..self.constants.num_partial_rounds {
            self.partial_round();
        }

        // Second half of full rounds
        for _ in 0..full_rounds_half {
            self.full_round();
        }
        
		//self.state[1]
		return self.state[1];
        
    }

    fn add_constants(&mut self) {
        // Add round constants
        for i in 0..self.state.len() {
            self.state[i] += self.constants.round_keys[i + self.pos];
        }
    }

    // MDS matrix multiplication
    fn matrix_mul(&mut self) {
        let mut result = [F::zero(); 3];

        for (i, val) in self.constants.mds_matrix.iter().enumerate() {
            let mut tmp = F::zero();
            for (j, element) in self.state.iter().enumerate() {
                tmp += val[j] * element
            }
            result[i] = tmp;
        }

        self.state = result;
    }

    fn full_round(&mut self) {
        let t = self.state.len();
        self.add_constants();

        // S-boxes
        for i in 0..t {
            self.state[i] = self.state[i].pow_vartime(&[5, 0, 0, 0]);
        }

        self.matrix_mul();

        // Update the position of the round constants that are added
        self.pos += self.state.len();
    }

    fn partial_round(&mut self) {
        self.add_constants();

        // S-box
        self.state[0] = self.state[0].pow_vartime(&[5, 0, 0, 0]);

        self.matrix_mul();

        // Update the position of the round constants that are added
        self.pos += self.state.len();
    }
}

use k256_consts::*;
use secq256k1::field::{field_secp};
//use k256::FieldBytes;

fn main() {
		let args: Vec<String> = env::args().collect();
        type Scalar = field_secp::FieldElement;
        let input = [
            Scalar::from_str_vartime(&args[1]).unwrap(),
            Scalar::from_str_vartime(&args[2]).unwrap(),
        ];

        let constants = PoseidonConstants::<FieldElement>::new(
            ROUND_CONSTANTS.to_vec(),
            vec![
                MDS_MATRIX[0].to_vec(),
                MDS_MATRIX[1].to_vec(),
                MDS_MATRIX[2].to_vec(),
            ],
            NUM_FULL_ROUNDS,
            NUM_PARTIAL_ROUNDS,
        );
        let mut poseidon = Poseidon::new(constants);

        let digest = poseidon.hash(&input);
		println!("{:?}",format!("{:?}", digest));
        //assert_eq!(
           // digest,
           // Scalar::from_bytes(&[
             //   68, 120, 17, 40, 199, 247, 48, 80, 236, 89, 92, 44, 207, 217, 83, 62, 184, 194,
              //  173, 48, 66, 119, 238, 98, 175, 232, 78, 234, 75, 101, 229, 148
            //])
           // .unwrap()
      //  );
    }

 
