;;; Directory Local Variables
;;; For more information see (info "(emacs) Directory Variables")

((python-mode
  (eval . (pipenv-activate))
  (flycheck-checker . python-mypy)))
