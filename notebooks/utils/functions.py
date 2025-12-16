import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc
import numpy as np
from sklearn.model_selection import learning_curve, StratifiedKFold


def plot_confusion_matrix(y_true, y_pred, title, target_names):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=target_names, yticklabels=target_names)
    plt.title(f'Matrice de Confusion : {title}')
    plt.ylabel('Réalité')
    plt.xlabel('Prédiction')
    plt.show()




def plot_multiclass_roc(y_test_bin, y_score, title, n_classes, target_names):
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    plt.figure(figsize=(8, 6))
    
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
        plt.plot(fpr[i], tpr[i], lw=2, 
                 label=f'ROC {target_names[i]} (area = {roc_auc[i]:.2f})')

    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Taux de Faux Positifs')
    plt.ylabel('Taux de Vrais Positifs')
    plt.title(f'Courbes ROC - {title}')
    plt.legend(loc="lower right")
    plt.show()




def plot_learning_curve(estimator, title, X, y, cv=3, n_jobs=-1, train_sizes=np.linspace(0.2, 1.0, 5)):
    """
    Affiche la courbe d'apprentissage avec StratifiedKFold pour éviter les erreurs de classe unique.
    """
    plt.figure(figsize=(8, 6))
    plt.title(f"Courbe d'apprentissage : {title}")
    plt.xlabel("Taille du training set")
    plt.ylabel("Score (Accuracy)")

    cv_strategy = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, 
        X, 
        y, 
        cv=cv_strategy,
        n_jobs=n_jobs, 
        train_sizes=train_sizes, 
        scoring='accuracy',
        error_score='raise'
    )

    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.grid()
    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1, color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r", label="Train score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g", label="Cross-validation score")
    plt.legend(loc="best")
    plt.show()