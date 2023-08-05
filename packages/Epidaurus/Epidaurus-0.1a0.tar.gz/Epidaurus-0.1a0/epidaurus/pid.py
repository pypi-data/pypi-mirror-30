# inspired by https://gist.github.com/chaosmail/8372717


class PID:
    _config = None
    _verbose = None

    _p_gain = None  # controller gain constant
    _i_gain = None  # controller integration constant
    _d_gain = None  # controller derivation constant

    _update_interval = -1  # update time in seconds
    _windup_guard = None

    _set_point = None  # target output
    _i_prev = 0
    _err_prev = 0

    _correction_shift_pre = None
    _correction_shift_post = None
    _correction_scale_fit = None
    _correction_scale_norm = None

    def __init__(self, config, verbose):
        self._config = config
        self._verbose = verbose
        if self._verbose:
            print("PID.__ini__ - initializing instance ('{}').".format(self._config))

        self._p_gain = self._config["p-gain"]
        self._d_gain = self._config["d-gain"]
        self._i_gain = self._config["i-gain"]
        self._update_interval = self._config["update-interval"]
        self._windup_guard = self._config["windup-guard"]

        self._correction_scale_fit = self._config["correction-scale-fit"]
        self._correction_scale_norm = self._config["correction-scale-norm"]
        self._correction_shift_post = self._config["correction-shift-post"]
        self._correction_shift_pre = self._config["correction-shift-pre"]

    def reset(self, input_value, set_point):
        self._set_point = set_point
        #self._err_prev = 0
        #self._i_prev = 0

    def update(self, input_value):
        # Error between the desired and actual output
        err = self._set_point - input_value

        # proportional input
        p_term = self._p_gain * err

        # Integration Input
        i_term = self._i_prev + err * self._update_interval
        if i_term > self._windup_guard:
            i_term = self._windup_guard
        elif i_term < -self._windup_guard:
            i_term = -self._windup_guard
        self._i_prev = i_term
        i_term = i_term * self._i_gain

        # Derivation Input
        d_term = self._d_gain * (err - self._err_prev) / self._update_interval

        self._err_prev = err

        # Calculate output
        output_value = p_term + i_term + d_term

        output_value = output_value + self._correction_shift_pre
        output_value = output_value * self._correction_scale_norm
        output_value = output_value * self._correction_scale_fit
        output_value = output_value + self._correction_shift_post

        return output_value
