#ifdef _WIN32
#include "../../src/common/stdint.h"
#else
#include <stdint.h>
#endif

#include "Python.h"
#include "numpy/npy_common.h"

#include "../../src/common/binomial.h"
#include "../../src/common/entropy.h"
#include "../../src/xorshift1024/xorshift1024.h"

typedef struct s_aug_state {
  xorshift1024_state *rng;
  binomial_t *binomial;

  int has_gauss, has_gauss_float, shift_zig_random_int, has_uint32;
  float gauss_float;
  double gauss;
  uint32_t uinteger;
  uint64_t zig_random_int;

} aug_state;

static inline uint32_t random_uint32(aug_state *state) {
  uint64_t temp;
  if (state->has_uint32) {
    state->has_uint32 = 0;
    return state->uinteger;
  }
  state->has_uint32 = 1;
  temp = xorshift1024_next(state->rng);
  state->uinteger = (uint32_t)(temp >> 32);
  return (uint32_t)(temp & 0xFFFFFFFFLL);
}

static inline uint64_t random_uint64(aug_state *state) {
  return xorshift1024_next(state->rng);
}

static inline uint64_t random_raw_values(aug_state *state) {
  return random_uint64(state);
}

static inline double random_double(aug_state *state) {
  return (random_uint64(state) >> 11) * (1.0 / 9007199254740992.0);
}

extern void set_seed(aug_state *state, uint64_t seed);

extern void set_seed_by_array(aug_state *state, uint64_t *vals, int count);

extern void jump_state(aug_state *state);

extern void entropy_init(aug_state *state);

extern void init_state(aug_state *state, uint64_t *state_value);
