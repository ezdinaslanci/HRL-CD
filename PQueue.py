import heapq


class PQueue:
    def __init__(self):
        self._queue = []

    def push(self, item, priority):
        if not self.ifExists(item):
            heapq.heappush(self._queue, (-priority, item))
        else:
            if self.deleteWorse(item, priority):
                heapq.heappush(self._queue, (-priority, item))

    def pop(self):
        return heapq.heappop(self._queue)[-1]

    def ifExists(self, item):
        return any(entry[1] == item for entry in self._queue)

    def deleteWorse(self, item, priority):
        if self.ifExists(item):
            worseList = [i for i, entry in enumerate(self._queue) if item == entry[1] and -priority < entry[0]]
            if len(worseList) > 0:
                del self._queue[worseList[0]]
                heapq.heapify(self._queue)
                return True
        return False

    def clear(self):
        self._queue.clear()

    def print(self):
        for i in range(len(self._queue)):
            print(-self._queue[i][0], self._queue[i][1].coordinates, self._queue[i][1].actionType)

    def ifEmpty(self):
        if not self._queue:
            return True
        else:
            return False

    def count(self):
        return len(self._queue)
