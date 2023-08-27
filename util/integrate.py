class Integrate(object):
    def __init__(self, function, start, end, divisions):
        self.function_ = function
        self.start_ = start
        self.end_ = end
        self.increments_ = (end-start) / divisions

    def calc(self):
        res = 0.0

        x1 = self.start_
        y1 = self.function_(x1)

        while(x1 < self.end_):
            x2 = x1 + self.increments_

            y2 = self.function_(x2)

            interval = min(y1, y2) * self.increments_  # square portion
            interval += abs(y1 - y2) * self.increments_ * 0.5  # triangle portion
            res += interval

            x1 = x2
            y1 = y2

        return res
