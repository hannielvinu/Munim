def rupees(paise): return f'{paise//100}.{paise%100:02d}'
def template(move,language='en'):
    if move.offer is None: return move.hint
    lines='; '.join(f'{l.item} x{l.qty} at Rs {rupees(l.unit_price)} each' for l in move.offer.lines)
    start=('Manzoor' if language=='hi' else 'Accepted') if move.kind=='accept' else ('Aapka offer' if language=='hi' else 'Your offer')
    return f'{start}: {lines}. Total Rs {rupees(move.offer.total)}.'+(' Final offer.' if move.final else '')+(' '+move.hint if move.hint else '')
def validate(text,move,language='en'):
    # Exact template validation rejects novel item claims, even with matching numbers.
    return text==template(move,language)
def render(move,language='en',llm=None):
    safe=template(move,language)
    if llm:
        for _ in range(2):
            try:
                phrased=llm('Return this commerce statement exactly, without extra claims: '+safe)
                if validate(phrased,move,language): return phrased
            except Exception: pass
    return safe

