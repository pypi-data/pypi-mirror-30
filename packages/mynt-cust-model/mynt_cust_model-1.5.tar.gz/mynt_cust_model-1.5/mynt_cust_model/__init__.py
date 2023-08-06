import numpy as np

class Model():
    def __init__(self, gender, article_type, xg_model):
        self.model = xg_model
        
        self.word2vec = [('Men','Tshirts'),('Men','Shirts'), ('Men', 'Jeans'), \
        ('Men','Trousers'), ('Women','Jeans'),('Women','Kurtas')]
        
        self.gender = gender
        self.article_type = article_type

        self.user_vector_lengths = {
            ('Men','Jackets') : 39,
            ('Men','Sweatshirts') : 39,
            ('Men','Sweaters') : 39,
            ('Men','Blazers') : 39,
            ('Men','Kurtas') : 39,
            ('Men','Shorts') : 37,
            ('Women','Shorts') : 37,
            ('Women','Sweaters') : 39,            
            ('Women','Sweatshirts') : 39,
            ('Women','Jackets') : 39,
            ('Women','Tunics') : 43,
            ('Women','Kurtis') : 43,
            ('Women','Tshirts') : 39,
            ('Women','Shirts') : 39,
            ('Women', 'Dresses') : 43,
            ('Women', 'Tops') : 43 
        }

        self.style_vector_lengths = {   
            ('Men', 'Blazers'): 103,
            ('Men', 'Casual Shoes'): 101,
            ('Men', 'Flip Flops'): 101,
            ('Men', 'Formal Shoes'): 101,
            ('Men', 'Jackets'): 103,
            ('Men', 'Jeans'): 102,
            ('Men', 'Kurtas'): 103,
            ('Men', 'Sandals'): 101,
            ('Men', 'Shirts'): 103,
            ('Men', 'Shorts'): 102,
            ('Men', 'Sports Sandals'): 101,
            ('Men', 'Sports Shoes'): 101,
            ('Men', 'Sweaters'): 103,
            ('Men', 'Sweatshirts'): 103,
            ('Men', 'Trousers'): 102,
            ('Men', 'Tshirts'): 103,
            ('Women', 'Casual Shoes'): 101,
            ('Women', 'Dresses'): 105,
            ('Women', 'Flats'): 101,
            ('Women', 'Heels'): 101,
            ('Women', 'Jackets'): 105,
            ('Women', 'Jeans'): 102,
            ('Women', 'Kurtas'): 105,
            ('Women', 'Kurtis'): 105,
            ('Women', 'Shirts'): 105,
            ('Women', 'Shorts'): 102,
            ('Women', 'Sports Shoes'): 101,
            ('Women', 'Sweaters'): 105,
            ('Women', 'Sweatshirts'): 105,
            ('Women', 'Tops'): 105,
            ('Women', 'Tshirts'): 105,
            ('Women', 'Tunics'): 105
        }

    def get_prediction(self,user_vector, style_dict):
        gender = self.gender
        article_type = self.article_type

        predicted_sku = None

        if article_type in ['Casual Shoes', 'Formal Shoes', 'Casual Shoes', 'Heels', 'Sports Shoes', 'Flats',
                            'Flip Flops', 'Sports Sandals', 'Sandals']:
            main_diff = 1
        else:
            main_diff = 2

        if user_vector == None:
            return None
        
        #u_main_dim = self.get_main_dimension(user_vector)

        try:
            u_main_dim = user_vector[100]
        except:
            return None

        v_list = []
        diff_list = []
        predicted_sku_list = []
        for p_sku_id in style_dict:
            
            try:
                main_dim = style_dict[p_sku_id][100]
            except:
                return None
        
            if abs(main_dim - u_main_dim) <= main_diff:
                test_vector = list(user_vector) + list(style_dict[p_sku_id]) 
                v_list.append(test_vector)
                predicted_sku_list.append(p_sku_id)
                diff_list.append(abs(main_dim - u_main_dim))

        if len(v_list) <= 0:
            return None

        if min(diff_list) > main_diff:
            return None

        v_list = np.array(v_list)

        try:
            pro = self.model.predict_proba(v_list)
        except:
            return None
        predicted_pro = [x[1] for x in pro]
        i = np.argmax(predicted_pro)
        if predicted_pro[i] >= 0.5:
            predicted_sku = predicted_sku_list[i]
        else:
            predicted_sku = None

        return predicted_sku

    def get_main_dimension(self,user_vector):
        gender = self.gender
        article_type = self.article_type

        if (gender, article_type) in self.word2vec:
            return user_vector[100]
        else:
            u1 = user_vector[32]
            l = self.user_vector_lengths[(gender, article_type)]
            u2 = user_vector[l + 100]
            if u1 < 1.0:
                return u2
            return u1 