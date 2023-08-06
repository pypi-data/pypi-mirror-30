

(defn parse-indexing [sym]
  (if (not (in ":" sym)) 
      sym
      (do
        (setv splited (.split sym ":"))
        (list (map (fn [el]
                     (if (or (not el) (= el "\ufdd0"))
                         None
                         (do
                           (setv iel (try
                                       (int el)
                                       (except [e Exception] 
                                         None)))
                           (if iel
                               iel
                               (HySymbol el)))))
                   splited)))))

(defun parse-str-indexing (str-i)
  (let ((splited (.split str-i ":")))
    (list (map (fn [i] (get (hy.lex.tokenize i) 0)) splited))))

(defmacro nget [ar &rest indices]
  `(get ~ar ~(list-comp
               (cond
                 [(or (symbol? i) (keyword? i)) `(slice ~@(parse-indexing i))]
                 [(string? i) (parse-str-indexing i)]
                 [True i])               
               [i indices])))
