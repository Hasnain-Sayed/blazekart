def adjust_to_stock(product,requested_qty):
    if requested_qty > product.stock:
        return product.stock,True
    return requested_qty,False