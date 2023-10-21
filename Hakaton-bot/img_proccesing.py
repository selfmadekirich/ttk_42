import re
from PIL import Image
import cv2
import pytesseract
from pypdfium2 import pypdfium2
import numpy as np

class ImgProccessor:

    def __rotatate__(self,img,angle):
        (h, w) = img.shape[:2]
        (cX, cY) = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
        return cv2.warpAffine(img, M, (w, h))
    
    def __resize__(self,img,scale_percent):
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        return cv2.resize(img, dim, interpolation = cv2.INTER_AREA) 

    def __resize__(self,img,scale_w,scale_h):
        width = int(img.shape[1] * scale_w)
        height = int(img.shape[0] * scale_h)
        dim = (width, height)
        print(dim)
        return cv2.resize(img, dim, interpolation = cv2.INTER_AREA)  

    def __get_resize_scale__(self,img):
       # if img.shape[1] * img.shape[0] < 500000:
        #    return (1.25,1.25)
       # if img.shape[1] * img.shape[0] < 1000000:
        #    return (1,1)
        # 2500,1456
        # 720 480 
        #
        #
        ex_w,ex_h = 720,480
        w,h = 0,0
        if img.shape[1] > ex_w:
            w = ex_w / img.shape[1]
        else:
            w = img.shape[1] / ex_w

        if img.shape[0] > ex_h:
            h = ex_h / img.shape[0]
        else:
            h = img.shape[0] / ex_h

        return (w,h)
        
    def __get_structred_seria_and_number__(self,str_data):
        number = re.search(r"(\d{6})",str_data).group(0)
        seria = re.search(r"(\b\d{2}\s+\d{2})",str_data).group(0).replace('\n',' ')
        return {"seria":seria,"number":number}

    def __try_extract_passport_data__(self,img_str):
        img = cv2.imread(img_str)
        
        scale_percent = self.__get_resize_scale__(img)
       
        resized = self.__resize__(img,scale_percent[0],scale_percent[1])
        cv2.imshow('dd',resized)
        cv2.waitKey(0)
        for sigma_r in range(25,40,5): 
            dst = cv2.detailEnhance(resized, sigma_s=10, sigma_r=sigma_r / 100)
            for angle in [0,90,180,270]:
                r = self.__rotatate__(dst,angle)
                cv2.imshow('dd',r)
                cv2.waitKey(0)
                img_rgb = cv2.cvtColor(r, cv2.COLOR_BGR2RGB)
                parsed_img = pytesseract.image_to_string(img_rgb,lang='rus')
                print("parsed_img:"+parsed_img)
                result = re.search(r"(\d{6}\s+\d{2}\s+\d{2})|(\d{2}\s+\d{2}\s+\d{6})",parsed_img)
                if result:
                    return {"type":"passport","data":self.__get_structred_seria_and_number__(result.group(0))}
        return None
    def __get_structred_train_data__(self,str_data):
        parsed_data = re.search(r"((\d{3}[А-Я]?)\s+(\d{2})\s+(\d{3}))",str_data)
        return {"train":parsed_data.group(2), "wagon":parsed_data.group(3), "place":parsed_data.group(4)}
    
    def __pdf_to_img__(self,pdf_file):
         pdf = pypdfium2.PdfDocument(pdf_file)
         pil_image = pdf.get_page(0).render().to_pil()
         t = np.array(pil_image.convert('RGB'))
         t = t[:, :, ::-1].copy() 
         return t
    
    def __try_extract_train_data__(self,img_str):
        if img_str.endswith(".pdf"):
            img = self.__pdf_to_img__(img_str)
        else:
            img = cv2.imread(img_str)
        #cv2.imshow('tt',img)
        #cv2.waitKey(0)
        dst = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)
        #cv2.imshow('tt',dst)
        #cv2.waitKey(0)
        img_rgb = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)
        parsed_img = pytesseract.image_to_string(img_rgb,lang='rus')
        #print(parsed_img)
        result = re.search(r"(\d{3}[А-Я]?\s+\d{2}\s+\d{3})",parsed_img)
        if result:
            return {"type":"train","data":self.__get_structred_train_data__(result.group(0))}

    def try_extract_data(self,img_str):
        
        img_cv = cv2.imread(img_str)
        scale_percent = self.__get_resize_scale__(img_cv)
        resized = self.__resize__(img_cv,scale_percent[0],scale_percent[1])
        cv2.imshow('pic',resized)
        cv2.waitKey(0)
        # порог следует перебирать в цикле от 0.10 до 0.4 - дальше смысла нет
        dst = cv2.detailEnhance(resized, sigma_s=10, sigma_r=0.35)
        dst = dst[int(dst.shape[0]/2):int(dst.shape[0])]
        cv2.imshow('pic',dst)
        cv2.waitKey(0)
        resized = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
        r = self.__rotatate__(dst,180)
        cv2.imshow('pic',r)
        cv2.waitKey(0)
      
        img_rgb = cv2.cvtColor(r, cv2.COLOR_BGR2RGB)

        parsed_img = pytesseract.image_to_string(img_rgb,lang='rus')

        result = re.search(r"(\d{6}\s+\d{2}\s+\d{2})|(\d{2}\s+\d{2}\s+\d{6})",parsed_img)
        print(parsed_img) 
        print(result)
         
        
        '''
        print(img_str)
        result = self.__try_extract_train_data__(img_str)
        print(result)
        result_data = self.__try_extract_passport_data__(img_str)
        print(result_data)
        if result_data:
            return result_data
        if result:
            return result
        '''
        raise Exception('failed to parse!')

#c = ImgProccessor()
#print('here:' + str(c.try_extract_data('chat_672125750/photo.png')))
#print('here:' + str(c.try_extract_data('../test_img/my.png')))
