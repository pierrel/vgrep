(defun async-command-to-org-buffer (command buffer-name)
  (let ((output-buffer (generate-new-buffer buffer-name)))
    (make-process
     :name "vgrep-async-command"
     :buffer output-buffer
     :command (list shell-file-name
		    shell-command-switch
		    command))
    (display-buffer output-buffer)
    (with-current-buffer output-buffer
      (org-mode))))

(defun vgrep (query)
  (interactive "squery: \n")
  (async-command-to-org-buffer (format "vgrep -q \"%s\"" query)
			       "*vgrep search*"))
