from Utilities.GraphView import (
    bars_html,
    sorted_row,
    compare_phase,
    heap_frame,
    merge_dot,
    merge_array_html,
)


class SortAlgorithm:
    def __init__(self, name, t_complexity=None, s_complexity=None, description=None):
        self._name = name
        self._t_complexity = t_complexity   # time-complexity string, e.g. "O(n²)"
        self._s_complexity = s_complexity   # space-complexity string, e.g. "O(1)"
        self._description = description      # one-line summary of the algorithm

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def t_complexity(self):
        return self._t_complexity

    @t_complexity.setter
    def t_complexity(self, value):
        self._t_complexity = value

    @property
    def s_complexity(self):
        return self._s_complexity

    @s_complexity.setter
    def s_complexity(self, value):
        self._s_complexity = value

    def animate_sort(self, array):
        # Default visualisation (Bubble / Insertion): a bar chart that auto-plays
        # frame by frame — same {phase, graphviz, html} contract the page renders
        # for the graphviz sorts, so no Play/Pause buttons are needed. A "Sorted"
        # accumulator row below the bars fills as elements lock into place, the
        # way Heap's extracted elements drop into its sorted-output row.
        # Default visualisation (Bubble / Insertion): a bar chart that auto-plays
        # frame by frame — same {phase, graphviz, html} contract the page renders
        # for the graphviz sorts, so no Play/Pause buttons are needed. A "Sorted"
        # accumulator row below the bars fills as elements lock into place, the
        # way Heap's extracted elements drop into its sorted-output row.
        arr = array.copy()
        self.validate(arr)
        n = len(arr)
        maxval = max(arr) if arr else 0

        def frame(state, highlights, sorted_idx, phase):
            s = set(sorted_idx)
            return {
                "phase": phase,
                "graphviz": None,
                "html": bars_html(state, highlights, maxval, s) + sorted_row(state, s),
            }

        frames = [frame(arr, [], (), "Initial array")]
        for item in self.sort(arr):
            # sorts may yield (state, highlights) or (state, highlights, sorted)
            if len(item) == 3:
                state, highlights, sorted_idx = item
            else:
                state, highlights = item
                sorted_idx = ()
            frames.append(frame(state, highlights, sorted_idx, compare_phase(highlights)))
        frames.append(frame(arr, [], range(n), "Sorted"))
        return frames
        
    def __str__(self):
        return self._name
        return self._name

    def __repr__(self):
        return self._name

    def __parse(self, value):
        if isinstance(value, bool):
            raise ValueError(f"{value} is not a Number.")
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            s = value.strip()
            try:
                return int(s)
            except ValueError: 
                return float(s)
        raise TypeError(f"Unsupported Element: {type(value).__name__}.")

    def validate(self, array):
        try:
            """
                This parses the input array and checks for the following:
                    1. if array is valid array
                    2. if each value in the array is strictly int/float

                If array parameter happens to be a stringified-array/array of strings of integers:
                    1. parse them
                    2. change it to array of int/floats in place

                All operations does not return any values, just manipulating the array param in place
            """
            if not isinstance(array, list):
                raise TypeError(f"Expected an Array, got {type(array).__name__}")
            for i, value in enumerate(array):
                array[i] = self.__parse(value)
            
        except:
            return f"NAWWWW"
        
    
    def sort(self, array):
        raise NotImplementedError


class BubbleSort(SortAlgorithm):
    # O(n²) — nested comparisons; O(1) — in-place, no extra memory
    def __init__(self):
        super().__init__(
            "Bubble Sort", t_complexity="O(n\u00b2)", s_complexity="O(1)",
            description="Repeatedly swaps adjacent out-of-order pairs, "
                        "bubbling the largest value to the end each pass.",
        )

    def sort(self, array):
        self.validate(array)

        length = len(array)
        n = length
        sorted_from = length  # indices >= sorted_from are locked in final position
        swapped = True
        while swapped:
            swapped = False
            new_n = 0
            for i in range(1, n):
                yield array, [i-1, i], range(sorted_from, length)
                first_num = array[i-1]
                second_num = array[i]
                if first_num > second_num:
                    array[i-1], array[i] = array[i], array[i-1]
                    swapped = True
                    new_n = i

                    yield array, [i-1, i], range(sorted_from, length)
            # after a pass, everything from the last swap onward is in place
            n = new_n
            sorted_from = new_n


class InsertionSort(SortAlgorithm):
    def __init__(self):
        super().__init__(
            "Insertion Sort", t_complexity="O(n\u00b2)", s_complexity="O(1)",
            description="Grows a sorted prefix, inserting each next element "
                        "into its correct position among the sorted items.",
        )

    def sort(self, array):
        self.validate(array)
        n = len(array)
        for outerIndex in range(1, n):
            innerIndex = outerIndex
            temp = array[innerIndex]
            while (innerIndex > 0) and (temp < array[innerIndex - 1]):
                # comparing/shifting temp against the element on its left
                # ([0, outerIndex) is the sorted-so-far prefix being inserted into)
                yield array, [innerIndex - 1, innerIndex], range(0, outerIndex)
                array[innerIndex] = array[innerIndex - 1]
                innerIndex -= 1
                yield array, [innerIndex, innerIndex + 1], range(0, outerIndex)
            array[innerIndex] = temp
            yield array, [innerIndex], range(0, outerIndex + 1)


class HeapSort(SortAlgorithm):
    def __init__(self):
        super().__init__(
            "Heap Sort", t_complexity="O(n log n)", s_complexity="O(1)",
            description="Builds a max-heap, then repeatedly extracts the "
                        "largest element to the end and re-heapifies.",
        )

    def _leftChild(self, index):
        return 2 * index + 1

    def _rightChild(self, index):
        return 2 * index + 2

    def _max_heapify(self, arr, index, size, phase):
        # Sift `index` down through the heap region [0, size); yields a
        # (snapshot, highlights, meta) triple per level so animate_sort can
        # render each comparison/swap as its own frame.
        while self._leftChild(index) < size:
            left = self._leftChild(index)
            right = self._rightChild(index)
            if right >= size:
                max_child_idx = left
            else:
                max_child_idx = left if arr[left] > arr[right] else right
            if arr[max_child_idx] > arr[index]:
                arr[index], arr[max_child_idx] = arr[max_child_idx], arr[index]
            yield arr, [index, max_child_idx], {
                "phase": f"{phase}: sift index {index} ↔ child {max_child_idx}",
                "heap_size": size,
            }
            index = max_child_idx

    def _build_max_heap(self, array):
        n = len(array)
        start_index = (n // 2) - 1
        while start_index >= 0:
            yield from self._max_heapify(
                array, start_index, n, f"Build heap (sift from {start_index})"
            )
            start_index -= 1

    def sort(self, array):
        self.validate(array)

        yield from self._build_max_heap(array)
        yield array, [], {"phase": "Max-heap built", "heap_size": len(array)}
        heap_end_pos = len(array) - 1
        while heap_end_pos > 0:
            array[0], array[heap_end_pos] = array[heap_end_pos], array[0]
            yield array, [0, heap_end_pos], {
                "phase": f"Extract max → lock position {heap_end_pos}",
                "heap_size": heap_end_pos,
            }
            yield from self._max_heapify(array, 0, heap_end_pos, "Re-heapify root")
            heap_end_pos -= 1
        yield array, [], {"phase": "Sorted", "heap_size": 0}

    def animate_sort(self, array):
        arr = array.copy()
        self.validate(arr)
        n = len(arr)
        frames = [heap_frame(arr, [], n, "Initial array")]  # bottom starts empty
        for state, highlights, meta in self.sort(arr):
            frames.append(heap_frame(state, highlights, meta["heap_size"], meta["phase"]))
        return frames



class MergeSort(SortAlgorithm):
    # O(n log n) — divide-and-conquer with log n levels each merging O(n); O(n) — temporary arrays during merge
    def __init__(self):
        super().__init__(
            "Merge Sort", t_complexity="O(n log n)", s_complexity="O(n)",
            description="Recursively splits the array in half, then merges "
                        "the sorted halves back together.",
        )

    def sort(self, array, left=None, right=None):
        # In-place top-down merge over index ranges [left, right). Operating on
        # absolute indices (instead of list copies) gives every recursive call
        # a stable identity "left_right", so the recursion tree keeps fixed node
        # positions across frames. Yields (snapshot, highlights, meta) triples.
        self.validate(array)

        if left is None:
            left, right = 0, len(array)

        if right - left <= 1:
            yield array, [], {"event": "leaf", "node": (left, right),
                              "phase": f"Base case [{left},{right}) — trivially sorted"}
            return

        mid = (left + right) // 2
        yield array, [], {"event": "split", "node": (left, right),
                          "left": (left, mid), "right": (mid, right),
                          "phase": f"Split [{left},{right}) → [{left},{mid}) + [{mid},{right})"}

        yield from self.sort(array, left, mid)
        yield from self.sort(array, mid, right)

        leftArr = array[left:mid]
        rightArr = array[mid:right]
        leftIndex = rightIndex = 0
        writeIndex = left
        while leftIndex < len(leftArr) and rightIndex < len(rightArr):
            if leftArr[leftIndex] <= rightArr[rightIndex]:
                array[writeIndex] = leftArr[leftIndex]
                leftIndex += 1
            else:
                array[writeIndex] = rightArr[rightIndex]
                rightIndex += 1
            yield array, [writeIndex], {"event": "write", "node": (left, right),
                               "phase": f"Merge into [{left},{right}): write {array[writeIndex]} at index {writeIndex}"}
            writeIndex += 1
        while leftIndex < len(leftArr):
            array[writeIndex] = leftArr[leftIndex]
            yield array, [writeIndex], {"event": "write", "node": (left, right),
                               "phase": f"Merge into [{left},{right}): write {array[writeIndex]} at index {writeIndex}"}
            leftIndex += 1
            writeIndex += 1
        while rightIndex < len(rightArr):
            array[writeIndex] = rightArr[rightIndex]
            yield array, [writeIndex], {"event": "write", "node": (left, right),
                               "phase": f"Merge into [{left},{right}): write {array[writeIndex]} at index {writeIndex}"}
            rightIndex += 1
            writeIndex += 1

        yield array, [], {"event": "merged", "node": (left, right),
                          "phase": f"Merged [{left},{right})"}


    def animate_sort(self, array):
        arr = array.copy()
        self.validate(arr)
        n = len(arr)
        nodes = {f"0_{n}": (0, n)}
        merged = set()
        completed = [False] * n  # indices locked into a completed sorted run
        frames = [{
            "phase": "Initial array",
            "graphviz": merge_dot(arr, nodes, merged, None),
            "html": merge_array_html(arr, None, None, completed),
        }]
        for state, highlights, meta in self.sort(arr):
            node_start, node_end = meta["node"]
            node_id = f"{node_start}_{node_end}"
            nodes.setdefault(node_id, (node_start, node_end))
            event = meta["event"]
            if event == "split":
                for child_start, child_end in (meta["left"], meta["right"]):
                    nodes.setdefault(f"{child_start}_{child_end}", (child_start, child_end))
                html = merge_array_html(state, (node_start, node_end), None, completed)
            elif event == "write":
                write_index = highlights[0]
                html = merge_array_html(state, (node_start, node_end), write_index, completed)
            else:  # merged / leaf
                merged.add(node_id)
                if event == "merged":               # only real merges lock green
                    for index in range(node_start, node_end):
                        completed[index] = True
                html = merge_array_html(state, None, None, completed)
            frames.append({
                "phase": meta["phase"],
                "graphviz": merge_dot(state, nodes, merged, node_id),
                "html": html,
            })
        return frames


class QuickSort(SortAlgorithm):
    # Divide-and-conquer (Week 3): pick a pivot, partition the array so smaller
    # values sit left and larger values right, then recurse on each side. Lomuto
    # scheme (last element as pivot). O(n log n) average with balanced splits;
    # O(n²) worst (e.g. already-sorted input) — the headline metric shows the
    # average. O(log n) auxiliary space for the recursion stack.
    def __init__(self):
        super().__init__(
            "Quick Sort", t_complexity="O(n log n)", s_complexity="O(log n)",
            description="Picks a pivot and partitions the array into smaller / "
                        "larger around it (Lomuto), then recurses on each side.",
        )

    def sort(self, array):
        self.validate(array)
        # `locked` accumulates indices whose value has reached its final sorted
        # position; every partition locks its pivot there.
        yield from self._quicksort(array, 0, len(array) - 1, set())

    def _quicksort(self, array, low, high, locked):
        # Recursively sort array[low..high] in place, yielding the shared
        # (state, highlights, locked) frames so the inherited bar-chart
        # animate_sort renders each comparison (highlighted pair) and swap just
        # like Bubble/Insertion.
        if low > high:
            return
        if low == high:
            locked.add(low)
            return

        pivot = array[high]                        # Lomuto: last element is the pivot
        i = low - 1                                # boundary of the "< pivot" region
        for j in range(low, high):
            yield array, [j, high], locked         # compare array[j] against the pivot
            if array[j] < pivot:
                i += 1
                if i != j:
                    array[i], array[j] = array[j], array[i]
                    yield array, [i, j], locked    # swap into the smaller region

        pivot_index = i + 1
        if pivot_index != high:
            array[pivot_index], array[high] = array[high], array[pivot_index]
            yield array, [pivot_index, high], locked   # move pivot to its final slot
        locked.add(pivot_index)                    # pivot is now in its final position
        yield array, [pivot_index], locked

        yield from self._quicksort(array, low, pivot_index - 1, locked)
        yield from self._quicksort(array, pivot_index + 1, high, locked)

