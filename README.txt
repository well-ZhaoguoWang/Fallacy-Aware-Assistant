Logic Checker — Fallacy-Aware-Assistant  https://github.com/well-ZhaoguoWang/Fallacy-Aware-Assistant.git


Evaluation datasets: CoCoLoFa and MAFALDA:

CoCoLoFa: An English corpus of online comments annotated for informal logical fallacies. It includes binary labels (fallacy / no fallacy)
and eight subtype categories, and is commonly used as a baseline for fallacy detection and fine-grained classification.  https://github.com/Crowd-AI-Lab/cocolofa/

MAFALDA: A multi-source English fallacy corpus with a hierarchical label scheme—Level 0 (fallacy / no fallacy),
Level 1 (three macro-categories: Pathos / Ethos / Logos), and Level 2 (23 fine-grained types). It supports span-based
and disjunctive evaluation to handle multi-label and ambiguous cases.    https://github.com/ChadiHelwe/MAFALDA

Please unzip my project, then open Google Chrome. Click the four-dot icon in the top-right corner, choose Extensions,
then Manage Extensions, click Load unpacked, select ex folder and select checker folder, and run flask_app.py in the main directory.

1) A floating window will appear. You can copy and paste any news context and comment to detect fallacies.
The window can be minimized or closed.

2) Open any Reddit post, right-click, and choose Batch Analyze (reddit only) to automatically analyze all comments in the thread.
(Due to platform API limitations, Reddit is currently the only supported platform.)

3) On any webpage, select a sentence, right-click, and choose Start checking for fallacies to analyze the selected text.