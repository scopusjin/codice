from pathlib import Path

path = Path("app/graphing.py")
text = path.read_text(encoding="utf-8")

old = "I parametri del caso in esame ricadono al di fuori dei range di applicabilità dell’equazione di Henssge, che fornirebbe risultati non attendibili."
new = "Nel caso in esame, il grado di raffreddamento corporeo, calcolabile sulla base della temperatura rettale e ambientale, ricade al di fuori dei range nei quali il metodo di Henssge consente una stima sufficientemente attendibile del tempo post-mortale; la sua applicazione porterebbe pertanto a formulare stime tendenzialmente inaffidabili."

count = text.count(old)
if count != 1:
    raise SystemExit(f"Expected exactly one target phrase, found {count}")

path.write_text(text.replace(old, new, 1), encoding="utf-8")
