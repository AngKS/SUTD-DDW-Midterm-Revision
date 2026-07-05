"""Reference content for the Exercise 1 "information & code-along" guide.

Pure data — one entry per sorting algorithm featured on the Exercise 1 page, in
the same order as the algorithm selectbox. Each entry has a plain-English
summary, a step-by-step "how it works", best/average/worst time + space
complexity, a stability flag, and a runnable Python implementation (in-place,
ascending — matching the course convention) for students to code along with.
"""

GUIDES = [
    {
        "name": "Bubble Sort",
        "summary": "Repeatedly walk the list, swapping neighbouring pairs that are "
                   "out of order — the largest value 'bubbles' to the end each pass.",
        "how": (
            "1. Compare each **adjacent pair**; if the left one is bigger, **swap** them.\n"
            "2. After one full pass, the largest remaining value is parked at the end.\n"
            "3. Repeat over the shrinking unsorted prefix.\n"
            "4. If a whole pass makes **no swaps**, the list is already sorted — stop early."
        ),
        "best": "O(n)", "average": "O(n²)", "worst": "O(n²)", "space": "O(1)",
        "stable": True,
        "code": (
            "def bubble_sort(array):\n"
            "    n = len(array)\n"
            "    for i in range(n - 1):\n"
            "        swapped = False\n"
            "        # after pass i, the last i items are already in place\n"
            "        for j in range(n - 1 - i):\n"
            "            if array[j] > array[j + 1]:        # adjacent pair out of order?\n"
            "                array[j], array[j + 1] = array[j + 1], array[j]\n"
            "                swapped = True\n"
            "        if not swapped:                        # nothing moved -> sorted\n"
            "            break\n"
            "    return array"
        ),
    },
    {
        "name": "Insertion Sort",
        "summary": "Grow a sorted prefix one item at a time, inserting each new item "
                   "into its correct place among the already-sorted items.",
        "how": (
            "1. Treat the first item as a sorted prefix of length 1.\n"
            "2. Take the next item as the **key**.\n"
            "3. **Shift** every sorted item bigger than the key one slot to the right.\n"
            "4. Drop the key into the gap. Repeat until the whole list is the prefix."
        ),
        "best": "O(n)", "average": "O(n²)", "worst": "O(n²)", "space": "O(1)",
        "stable": True,
        "code": (
            "def insertion_sort(array):\n"
            "    for i in range(1, len(array)):\n"
            "        key = array[i]                         # the item to insert\n"
            "        j = i - 1\n"
            "        while j >= 0 and array[j] > key:       # shift larger items right\n"
            "            array[j + 1] = array[j]\n"
            "            j -= 1\n"
            "        array[j + 1] = key                     # drop key into the gap\n"
            "    return array"
        ),
    },
    {
        "name": "Heap Sort",
        "summary": "Build a max-heap so the largest value sits at the root, then "
                   "repeatedly swap it to the end and re-heapify what remains.",
        "how": (
            "1. **Build a max-heap** from the array (`heapify` from the last parent up).\n"
            "2. The root is now the maximum — **swap** it with the last heap item.\n"
            "3. Shrink the heap by one and **sift the new root down** to restore order.\n"
            "4. Repeat until the heap is empty; the array is sorted ascending."
        ),
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)", "space": "O(1)",
        "stable": False,
        "code": (
            "def heapify(array, size, root):\n"
            "    largest = root\n"
            "    left, right = 2 * root + 1, 2 * root + 2\n"
            "    if left < size and array[left] > array[largest]:\n"
            "        largest = left\n"
            "    if right < size and array[right] > array[largest]:\n"
            "        largest = right\n"
            "    if largest != root:                        # a child is bigger -> sift down\n"
            "        array[root], array[largest] = array[largest], array[root]\n"
            "        heapify(array, size, largest)\n"
            "\n"
            "def heap_sort(array):\n"
            "    n = len(array)\n"
            "    for root in range(n // 2 - 1, -1, -1):     # build a max-heap\n"
            "        heapify(array, n, root)\n"
            "    for end in range(n - 1, 0, -1):            # extract the max repeatedly\n"
            "        array[0], array[end] = array[end], array[0]\n"
            "        heapify(array, end, 0)                 # re-heapify the rest\n"
            "    return array"
        ),
    },
    {
        "name": "Merge Sort",
        "summary": "Divide and conquer: split the list in half, sort each half "
                   "recursively, then merge the two sorted halves back together.",
        "how": (
            "1. **Divide**: split the list into two halves at the midpoint.\n"
            "2. **Conquer**: sort each half by calling merge sort on it (recursion).\n"
            "3. **Merge**: walk both sorted halves, always taking the smaller front item.\n"
            "4. A list of length 0 or 1 is the base case — already sorted."
        ),
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)", "space": "O(n)",
        "stable": True,
        "code": (
            "def merge_sort(array):\n"
            "    if len(array) <= 1:                        # base case: already sorted\n"
            "        return array\n"
            "    mid = len(array) // 2\n"
            "    left = merge_sort(array[:mid])             # sort the left half\n"
            "    right = merge_sort(array[mid:])            # sort the right half\n"
            "    return merge(left, right)                  # merge the sorted halves\n"
            "\n"
            "def merge(left, right):\n"
            "    result, i, j = [], 0, 0\n"
            "    while i < len(left) and j < len(right):\n"
            "        if left[i] <= right[j]:                # take the smaller front item\n"
            "            result.append(left[i]); i += 1\n"
            "        else:\n"
            "            result.append(right[j]); j += 1\n"
            "    result.extend(left[i:])                    # append whatever is left\n"
            "    result.extend(right[j:])\n"
            "    return result"
        ),
    },
    {
        "name": "Quick Sort",
        "summary": "Divide and conquer: pick a pivot, partition values into "
                   "smaller-than and larger-than groups around it, then recurse on each.",
        "how": (
            "1. Choose a **pivot** (here, the last element — the Lomuto scheme).\n"
            "2. **Partition**: scan the range, moving values `< pivot` to the left region.\n"
            "3. Swap the pivot into the boundary — it is now in its **final position**.\n"
            "4. Recurse on the left (`< pivot`) and right (`> pivot`) sub-ranges.\n"
            "Balanced pivots give O(n log n); a bad pivot (e.g. sorted input) gives O(n²)."
        ),
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n²)", "space": "O(log n)",
        "stable": False,
        "code": (
            "def quick_sort(array, low=0, high=None):\n"
            "    if high is None:\n"
            "        high = len(array) - 1\n"
            "    if low < high:\n"
            "        p = partition(array, low, high)        # pivot reaches its final index p\n"
            "        quick_sort(array, low, p - 1)          # sort the '< pivot' side\n"
            "        quick_sort(array, p + 1, high)         # sort the '> pivot' side\n"
            "    return array\n"
            "\n"
            "def partition(array, low, high):\n"
            "    pivot = array[high]                        # Lomuto: last element is the pivot\n"
            "    i = low - 1                                # boundary of the '< pivot' region\n"
            "    for j in range(low, high):\n"
            "        if array[j] < pivot:\n"
            "            i += 1\n"
            "            array[i], array[j] = array[j], array[i]\n"
            "    array[i + 1], array[high] = array[high], array[i + 1]\n"
            "    return i + 1"
        ),
    },
]

GUIDE_BY_NAME = {g["name"]: g for g in GUIDES}
