# maze-seeker
Repository for Artificial Intelligence - Group 5. We will be implementing a hide and seek game with autonomous agents for both hiding and seeking.

# Random algorithm without location retention
```
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|        |                 |  |           |     |
+  +--+  +  +--+--+--+--+  +  +  +  +--+  +--+  +
|  |        |     |        |     |  |  |     |  |
+  +--+--+--+  +  +  +--+--+  +--+  +  +--+  +  +
|        |     |  |  |        |     |           |
+--+--+  +  +--+  +  +--+--+--+  +--+--+--+--+  +
|     |  |     |  |  |        |        |     |  |
+  +  +  +--+  +  +  +  +--+  +--+--+  +  +  +  +
|  |     |     |  |     |  |        |     |  |  |
+  +--+  +  +--+  +--+--+  +--+--+  +  +--+  +  +
|  |     |  |  |     |        |     |     |  |  |
+  +--+--+  +  +--+--+  +--+--+  +--+--+--+  +  +
|  |     |  |        |           |           |  |
+  +  +  +  +  +  +--+  +--+--+--+--+  +--+--+  +
|     |     |  |                       |      01|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```
```
Steps Taken = 68925
Spots Visited = [51, 101, 151, 201, 202, 252, 251, 253, 254, 255, 256, 257, 258, 307, 308, 102, 152, 52, 358, 357, 407, 408, 458, 508, 457, 507, 558, 557, 556, 555, 554, 456, 455, 454, 405, 355, 404, 354, 353, 352, 351, 401, 402, 452, 502, 501, 451, 551, 552, 602, 652, 651, 601, 701, 702, 752, 751, 753, 754, 755, 704, 654, 655, 656, 705, 657, 658, 708, 758, 759, 760, 761, 710, 660, 711, 610, 661, 611, 561, 511, 461, 462, 460, 510, 560, 707, 757, 463, 464, 413, 414, 364, 363, 362, 361, 360, 310, 260, 261, 311, 262, 263, 264, 214, 164, 165, 163, 213, 166, 216, 266, 267, 317, 217, 367, 366, 316, 416, 466, 467, 417, 167, 517, 516, 566, 567, 568, 569, 570, 53, 54, 55, 56, 57, 107, 157, 158, 58, 108, 156, 159, 160, 110, 60, 61, 111, 161, 62, 155, 154, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 125, 175, 126, 176, 174, 173, 172, 171, 170, 220, 219, 270, 169, 269, 319, 369, 419, 370, 420, 470, 469, 320, 471, 472, 422, 423, 372, 373, 473, 374, 375, 376, 377, 378, 428, 379, 429, 479, 480, 478, 481, 482, 483, 484, 534, 485, 535, 584, 585, 583, 582, 632, 682, 681, 631, 680, 679, 678, 677, 676, 675, 674, 673, 623, 573, 574, 575, 572, 622, 672, 722, 772, 771, 770, 773, 723, 774, 769, 768, 767, 717, 716, 667, 668, 669, 670, 666, 665, 664, 614, 663, 714, 764, 763, 713, 766, 613, 564, 563, 581, 775, 776, 777, 778, 779, 780, 576, 525, 526, 476, 475, 577, 578, 579, 781, 782, 783, 784, 785, 786, 787, 737, 788, 738, 688, 687, 686, 685, 684, 689, 690, 691, 692, 693, 643, 644, 694, 593, 594, 544, 543, 493, 494, 444, 443, 393, 394, 392, 391, 390, 440, 441, 491, 490, 489, 488, 538, 438, 437, 388, 387, 487, 537, 587, 588, 386, 385, 384, 383, 382, 381, 331, 332, 282, 283, 284, 285, 235, 185, 184, 135, 134, 234, 281, 85, 86, 87, 88, 89, 84, 83, 90, 91, 141, 140, 191, 190, 82, 132, 182, 131, 181, 180, 179, 129, 128, 79, 78, 178, 228, 229, 278, 277, 276, 275, 274, 279, 81, 589, 590, 591, 192, 193, 243, 194, 244, 294, 293, 292, 295, 296, 346, 396, 446, 447, 397, 347, 497, 496, 547, 546, 596, 597, 647, 297, 247, 246, 196, 291, 290, 289, 288, 287, 238, 237, 188, 187, 197, 147, 146, 96, 97, 646, 696, 697, 746, 796]
Current Location = 796
```

# Random algorithm with location retention
```
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|           |                    |              |
+  +--+  +  +  +--+--+  +--+--+--+  +  +--+  +--+
|  |     |  |  |     |  |           |     |  |  |
+--+  +--+  +  +--+  +  +  +--+--+--+--+  +--+  +
|     |     |        |     |              |     |
+  +--+--+--+--+--+  +--+--+  +--+--+--+  +  +--+
|                 |  |  |     |        |  |     |
+--+--+--+--+--+  +  +  +  +--+  +--+--+  +--+  +
|                 |     |  |           |  |  |  |
+  +--+--+--+--+--+--+  +  +  +--+--+  +  +  +  +
|        |           |  |  |        |  |  |  |  |
+  +--+  +  +--+--+  +  +  +--+--+  +  +  +  +  +
|  |     |  |     |     |  |     |  |        |  |
+  +  +--+  +  +  +--+--+  +  +  +--+--+--+--+  +
|  |           |        |     |           01    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```
```
Steps Taken = 544
Spots Visited = [51, 101, 102, 152, 151, 52, 53, 54, 55, 56, 57, 107, 157, 158, 108, 58, 59, 60, 110, 111, 161, 160, 210, 260, 259, 258, 257, 261, 211, 61, 156, 155, 205, 255, 254, 204, 154, 253, 252, 302, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 417, 416, 466, 467, 465, 464, 463, 462, 461, 460, 459, 458, 457, 456, 455, 454, 453, 452, 502, 501, 451, 551, 601, 651, 701, 751, 752, 702, 652, 602, 552, 553, 554, 555, 556, 557, 607, 608, 658, 657, 656, 655, 654, 704, 705, 755, 756, 757, 758, 759, 760, 710, 660, 661, 611, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 620, 670, 669, 619, 671, 672, 673, 623, 622, 572, 573, 523, 473, 472, 471, 470, 469, 419, 420, 370, 369, 319, 269, 219, 220, 170, 169, 168, 167, 166, 270, 320, 268, 267, 266, 265, 264, 263, 213, 214, 164, 163, 113, 114, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 123, 173, 172, 122, 222, 272, 273, 223, 274, 275, 276, 226, 176, 175, 225, 177, 178, 179, 180, 181, 182, 183, 184, 185, 135, 85, 86, 87, 137, 187, 188, 138, 88, 89, 90, 91, 92, 93, 143, 144, 194, 193, 94, 95, 96, 97, 189, 190, 191, 241, 240, 290, 340, 341, 291, 391, 390, 440, 441, 491, 490, 540, 590, 591, 541, 641, 640, 690, 691, 692, 693, 643, 644, 694, 594, 593, 543, 544, 494, 493, 689, 688, 638, 637, 687, 587, 537, 538, 588, 488, 487, 486, 485, 484, 483, 482, 481, 480, 479, 529, 579, 578, 528, 478, 580, 581, 582, 583, 584, 634, 684, 685, 635, 585, 431, 381, 382, 432, 383, 384, 385, 386, 387, 388, 289, 288, 287, 286, 285, 284, 283, 282, 281, 280, 279, 329, 328, 278, 378, 377, 376, 426, 425, 375, 475, 525, 526, 476, 576, 575, 625, 626, 676, 726, 776, 775, 725, 675, 777, 778, 779, 729, 679, 680, 681, 682, 732, 782, 781, 731, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792]
Current Location = 792
```
