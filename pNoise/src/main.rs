// Converted to Rust script by David J.
// May-10-2023
// Original script https://gist.github.com/Flafla2/f0260a861be0ebdeef76

use image::{GrayImage, Luma};

pub struct Perlin {
    pub repeat: i32,
}

impl Perlin {
    pub fn new(repeat: i32) -> Perlin {
        Perlin { repeat }
    }

    pub fn octave_perlin(&self, x: f64, y: f64, z: f64, octaves: i32, persistence: f64) -> f64 {
        let mut total = 0.0;
        let mut frequency = 1.0;
        let mut amplitude = 1.0;
        let mut max_value = 0.0;

        for _ in 0..octaves {
            total += self.perlin(x * frequency, y * frequency, z * frequency) * amplitude;
            max_value += amplitude;
            amplitude *= persistence;
            frequency *= 2.0;
        }

        total / max_value
    }

    const PERMUTATION: [u8; 256] = [
        151, 160, 137, 91, 90, 15, 131, 13, 201, 95, 96, 53, 194, 233, 7, 225, 140, 36, 103, 30, 69,
        142, 8, 99, 37, 240, 21, 10, 23, 190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62, 94, 252, 219,
        203, 117, 35, 11, 32, 57, 177, 33, 88, 237, 149, 56, 87, 174, 20, 125, 136, 171, 168, 68, 175,
        74, 165, 71, 134, 139, 48, 27, 166, 77, 146, 158, 231, 83, 111, 229, 122, 60, 211, 133, 230,
        220, 105, 92, 41, 55, 46, 245, 40, 244, 102, 143, 54, 65, 25, 63, 161, 1, 216, 80, 73, 209,
        76, 132, 187, 208, 89, 18, 169, 200, 196, 135, 130, 116, 188, 159, 86, 164, 100, 109, 198,
        173, 186, 3, 64, 52, 217, 226, 250, 124, 123, 5, 202, 38, 147, 118, 126, 255, 82, 85, 212,
        207, 206, 59, 227, 47, 16, 58, 17, 182, 189, 28, 42, 223, 183, 170, 213, 119, 248, 152, 2,
        44, 154, 163, 70, 221, 153, 101, 155, 167, 43, 172, 9, 129, 22, 39, 253, 19, 98, 108, 110,
		79, 113, 224, 232, 178, 185, 112, 104, 218, 246, 97, 228, 251, 34, 242, 193, 238, 210, 144,
		12, 191, 179, 162, 241, 81, 51, 145, 235, 249, 14, 239, 107, 49, 192, 214, 31, 181, 199, 106,
		157, 184, 84, 204, 176, 115, 121, 50, 45, 127, 4, 150, 254, 138, 236, 205, 93, 222, 114, 67,
		29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156, 180,
	];

	fn p() -> [u8; 512] {
		let mut p = [0; 512];
		for i in 0..512 {
			p[i] = Self::PERMUTATION[i % 256];
		}
		p
	}

	pub fn perlin(&self, x: f64, y: f64, z: f64) -> f64 {
		let x = if self.repeat > 0 { x % self.repeat as f64 } else { x };
		let y = if self.repeat > 0 { y % self.repeat as f64 } else { y };
		let z = if self.repeat > 0 { z % self.repeat as f64 } else { z };

		let xi = (x as u32 & 255) as usize;
		let yi = (y as u32 & 255) as usize;
		let zi = (z as u32 & 255) as usize;
		let xf = x - x.floor();
		let yf = y - y.floor();
		let zf = z - z.floor();
		let u = Self::fade(xf);
		let v = Self::fade(yf);
		let w = Self::fade(zf);

		let p = Self::p();

		let aaa = p[p[p[xi] as usize + yi] as usize + zi] as usize;
		let aba = p[p[p[xi] as usize + Self::inc(yi, self.repeat)] as usize + zi] as usize;
		let aab = p[p[p[xi] as usize + yi] as usize + Self::inc(zi, self.repeat)] as usize;
		let abb = p[p[p[xi] as usize + Self::inc(yi, self.repeat)] as usize + Self::inc(zi, self.repeat)] as usize;
		let baa = p[p[p[Self::inc(xi, self.repeat)] as usize + yi] as usize + zi] as usize;
		let bba = p[p[p[Self::inc(xi, self.repeat)] as usize + Self::inc(yi, self.repeat)] as usize + zi] as usize;
		let bab = p[p[p[Self::inc(xi, self.repeat)] as usize + yi] as usize + Self::inc(zi, self.repeat)] as usize;
		let bbb = p[p[p[Self::inc(xi, self.repeat)] as usize + Self::inc(yi, self.repeat)] as usize + Self::inc(zi, self.repeat)] as usize;

		let x1 = Self::lerp(
			Self::grad(aaa, xf, yf, zf),
			Self::grad(baa, xf - 1.0, yf, zf),
			u,
		);
		let x2 = Self::lerp(
			Self::grad(aba, xf, yf - 1.0, zf),
			Self::grad(bba, xf - 1.0, yf - 1.0, zf),
			u,
		);
		let y1 = Self::lerp(x1, x2, v);

		let x1 = Self::lerp(
			Self::grad(aab, xf, yf, zf - 1.0),
			Self::grad(bab, xf - 1.0, yf, zf - 1.0),
			u,
		);
		let x2 = Self::lerp(
			Self::grad(abb, xf, yf - 1.0, zf - 1.0),
			Self::grad(bbb, xf - 1.0, yf - 1.0, zf - 1.0),
			u,
		);
		let y2 = Self::lerp(x1, x2, v);

		(Self::lerp(y1, y2, w) + 1.0) / 2.0
	}

	pub fn inc(n: usize, repeat: i32) -> usize {
		let mut num = n + 1;
		if repeat > 0 {
			num %= repeat as usize;
		}
		num
	}

	pub fn grad(hash: usize, x: f64, y: f64, z: f64) -> f64 {
		let h = hash & 15;
		let u = if h < 8 { x } else { y };
		let v = if h < 4 {
			y
		} else if h == 12 || h == 14 {
			x
		} else {
			z
		};

		let mut result = if (h & 1) == 0 { u } else { -u };
		result += if (h & 2) == 0 { v } else { -v };
		result
	}

	pub fn fade(t: f64) -> f64 {
		t * t * t * (t * (t * 6.0 - 15.0) + 10.0)
	}

	pub fn lerp(a: f64, b: f64, x: f64) -> f64 {
		a + x * (b - a)
	}

}

fn main() {
    let width = 512;
    let height = 512;
    let scale = 0.1; // Adjust this to change the scale of the noise
    let octaves = 6;
    let persistence = 0.00001;

    let perlin = Perlin::new(1234); // You can use any seed value
    let mut image = GrayImage::new(width, height);

    for y in 0..height {
        for x in 0..width {
            let nx = x as f64 * scale;
            let ny = y as f64 * scale;

            // Generate Perlin noise value
            let noise_value = perlin.octave_perlin(nx, ny, 0.0, octaves, persistence);

            // Normalize the value to the range [0, 255]
            let normalized_value = (((noise_value + 1.0) / 2.0) * 255.0).round() as u8;

            // Set the pixel value in the image
            image.put_pixel(x, y, Luma([normalized_value]));
        }
    }

    // Save the heightmap as a PNG
    image.save("heightmap.png").unwrap();
}