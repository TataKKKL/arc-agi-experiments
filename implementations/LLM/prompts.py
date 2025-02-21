PROMPT_REASONING = """
'You will be given some number of paired example inputs and outputs. The outputs were produced by applying a transformation rule to the inputs. In addition to the paired example inputs and outputs, there is also an additional input without a known output (or possibly multiple additional inputs). Your task is to determine the transformation rule and implement it in code.\n\nThe inputs and outputs are each "grids". A grid is a rectangular matrix of integers between 0 and 9 (inclusive). These grids will be shown to you as both images and grids of numbers (ASCII). You may also get an ASCII representation of the change for each cell comparing the input and output. For example 0 -> 1 means the value switched from 0 to 1 in that cell. `--` means the value in that cell did not change. The image and the grid of numbers for each input/output contain the same information: we just show both representations for convenience. Each number corresponds to a color in the image. The correspondence is as follows: black: 0, blue: 1, red: 2, green: 3, yellow: 4, grey: 5, pink: 6, orange: 7, purple: 8, brown: 9.\n\nThe transformation rule maps from each input to a single correct output, and your implementation in code must be exactly correct. Thus, you need to resolve all potential uncertainties you might have about the transformation rule. For instance, if the examples always involve some particular color being changed to another color in the output, but which color it is changed to varies between different examples, then you need to figure out what determines the correct output color. As another example, if some shape(s) or cells in the input are relocated or recolored, you need to determine which exact shapes should be relocated/recolored in the output and where they should be moved or what their color in the output should be. Whenever there are potential ambiguities or uncertainties in your current understanding of the transformation rule, you need to resolve them before implementing the transformation in code. You should resolve ambiguities and uncertainties by carefully analyzing the examples and using step by step reasoning.\n\nThe transformation rule might have multiple components and might be fairly complex. It\'s also reasonably common that the transformation rule has one main rule (e.g., replace cells in XYZ pattern with color ABC), but has some sort of exception (e.g., don\'t replace cells if they have color DEF). So, you should be on the lookout for additional parts or exceptions that you might have missed so far. Consider explicitly asking yourself (in writing): "Are there any additional parts or exceptions to the transformation rule that I might have missed?" (Rules don\'t necessarily have multiple components or exceptions, but it\'s common enough that you should consider it.)\n\nHere are some examples of transformation rules with multiple components or exceptions:\n\n- There is a grey grid with black holes that have different shapes and the rule is to fill in these holes with colored cells. Further, the color to use for each hole depends on the size of the hole (in terms of the number of connected cells). 1 cell holes are filled with pink, 2 cell holes are filled with blue, and 3 cell holes are filled with red.\n- The output is 3x3 while the input is 3x7. The output has red cells while the input has two "sub-grids" that are 3x3 and separated by a grey line in the middle. Each of the sub-grids has some colored cells (blue) and some black cells. The rule is to AND the two sub-grids together (i.e., take the intersection of where the two sub-grids are blue) and color the 3x3 cells in the output red if they are in the intersection and black otherwise.\n- The grey rectangular outlines are filled with some color in the output. Pink, orange, and purple are used to fill in the voids in different cases. The color depends on the size of the black void inside the grey outline where it is pink if the void has 1 cell (1x1 void), orange if the gap has 4 cells, and purple if the gap was 9 cells. For each void, all of the filled-in colors are the same.\n- The red shape in the input is moved. It is moved either horizontally or vertically. It is moved until moving it further would intersect with a purple shape. It is moved in the direction of the purple shape, that is, moved in whichever direction would involve it eventually intersecting with this purple shape.\n\nThese are just example rules; the actual transformation rule will be quite different. But, this should hopefully give you some sense of what transformation rules might look like.\n\nNote that in each of these cases, you would need to find the rule by carefully examining the examples and using reasoning. You would then need to implement the transformation rule precisely, taking into account all possible cases and getting all of the details right (e.g., exactly where to place various things or exactly which color to use in each case). If the details aren\'t fully ironed out, you should do additional reasoning to do so before implementing the transformation in code.\n\nYou\'ll need to carefully reason in order to determine the transformation rule. Start your response by carefully reasoning in <reasoning></reasoning> tags. Then, implement the transformation in code.\n\nYou follow a particular reasoning style. You break down complex problems into smaller parts and reason through them step by step, arriving at sub-conclusions before stating an overall conclusion. This reduces the extent to which you need to do large leaps of reasoning.\n\nYou reason in substantial detail for as long as is necessary to fully determine the transformation rule and resolve any ambiguities/uncertainties.\n\nAfter your reasoning, write code in triple backticks (```python and then ```).\nYou should write a function called `transform` which takes a single argument, the input grid as `list[list[int]]`, and returns the transformed grid (also as `list[list[int]]`).\nYour python code should not use libraries outside of the standard python libraries besides numpy.You can create helper functions.\nYou should make sure that you implement a version of the transformation which works in general (for inputs which have the same properties as the example inputs and the additional input(s)).\nDon\'t write tests in your python code, just output the `transform` function.'
"""