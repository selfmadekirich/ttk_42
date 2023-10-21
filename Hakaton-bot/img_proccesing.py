import re
from PIL import Image
import cv2
import pytesseract
from pypdfium2 import pypdfium2
import numpy as np
from imutils.contours import sort_contours
import imutils

class ImgProccessor:

    def __rotatate__(self,img,angle):
        (h, w) = img.shape[:2]
        (cX, cY) = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
        return cv2.warpAffine(img, M, (w, h))
    
    def __rotate_ex__(self,img,angle):
        size_reverse = np.array(img.shape[1::-1]) # swap x with y
        M = cv2.getRotationMatrix2D(tuple(size_reverse / 2.), angle, 1.)
        MM = np.absolute(M[:,:2])
        size_new = MM @ size_reverse
        M[:,-1] += (size_new - size_reverse) / 2.
        return cv2.warpAffine(img, M, tuple(size_new.astype(int)))
    
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
        if img.shape[1] * img.shape[0] < 500000:
            return (1.25,1.25)
        if img.shape[1] * img.shape[0] < 1000000:
            return (1,1)
        # 2500,1456
        # 720 480 
        '''
        ex_w,ex_h = 720,720
        if img.shape[1] < img.shape[0]:
            ex_w,ex_h = ex_h,ex_w
        w,h = 0,0
        if img.shape[1] > ex_w:
            w = ex_w / img.shape[1]
        else:
            w = img.shape[1] / ex_w

        if img.shape[0] > ex_h:
            h = ex_h / img.shape[0]
        else:
            h = img.shape[0] / ex_h
        '''
        return (0.15,0.15)
        
    def __get_structred_seria_and_number__(self,str_data):
        number = re.search(r"(\d{6})",str_data).group(0)
        seria = re.search(r"(\b\d{2}\s+\d{2})",str_data).group(0).replace('\n',' ')
        return {"seria":seria,"number":number}

    def __try_extract_passport_data__(self,img_str):
        img = cv2.imread(img_str)
        
        scale_percent = self.__get_resize_scale__(img)
       
        resized = self.__resize__(img,scale_percent[0],scale_percent[1])
        #cv2.imshow('dd',resized)
        #cv2.waitKey(0)
        for sigma_r in range(25,40,5): 
            dst = cv2.detailEnhance(resized, sigma_s=10, sigma_r=sigma_r / 100)
            for angle in [0,90,180,270]:
                r = self.__rotatate__(dst,angle)
            #    cv2.imshow('dd',r)
            #    cv2.waitKey(0)
                img_rgb = cv2.cvtColor(r, cv2.COLOR_BGR2RGB)
                parsed_img = pytesseract.image_to_string(img_rgb,lang='rus')
                #print("parsed_img:"+parsed_img)
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
        '''
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
        
        raise Exception('failed to parse!')
''' 
    def __get_blobs__(self,gray):
            
            rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 7))
            sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)
            cv2.imshow("Blackhat", blackhat)
            cv2.waitKey(0)
            grad = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
            grad = np.absolute(grad)
            (minVal, maxVal) = (np.min(grad), np.max(grad))
            grad = (grad - minVal) / (maxVal - minVal)
            grad = (grad * 255).astype("uint8")
            cv2.imshow("Gradient", grad)
            cv2.waitKey(0)
            grad = cv2.morphologyEx(grad, cv2.MORPH_CLOSE, rectKernel)
            thresh = cv2.threshold(grad, 0, 255,
	        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            cv2.imshow("Rect Close", thresh)
            cv2.waitKey(0)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
            thresh = cv2.erode(thresh, None, iterations=2)
            cv2.imshow("Square Close", thresh)
            cv2.waitKey(0)

            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	        cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            cnts = sort_contours(cnts, method="bottom-to-top")[0]
            return cnts

    
    def try_get_seria_number(self,img_str):
        img = cv2.imread(img_str)
        img =cv2.detailEnhance(img, sigma_s=10, sigma_r=0.45)
        scale_percent = self.__get_resize_scale__(img)
        resized = self.__resize__(img,scale_percent[0],scale_percent[1])
        cv2.imshow('resized',resized)
        cv2.waitKey(0)
        for angle in [0]: 
            r = self.__rotate_ex__(resized,angle)
           # r = r[int(r.shape[1] / 2):, 0:r.shape[0]]
            gray = cv2.cvtColor(r, cv2.COLOR_BGR2GRAY)
            cv2.imshow("Blackhat", gray)
            cv2.waitKey(0)
            (H, W) = gray.shape
            blobs = self.__get_blobs__(gray)
            mzrBox_name = None
            for c in blobs:
                (x, y, w, h) = cv2.boundingRect(c)
                percentWidth = w / float(W) 
                percentHeight = h / float(H)
                print(percentHeight,percentWidth)
                if(percentWidth > 0.5 and percentHeight > 0.04):
                    mzrBox_name=(x,y,w,h)
                    break

            if not mzrBox_name:
                 continue
            
            pX = int((x + w)*0.03)
            pY = int((y + h)*0.03)
            (x, y) = (x - pX, y - pY)
            (w, h) = (w + (pX * 2), h + (pY * 2))
            if(x<=0 or y<=0):
                   continue
            mrz = r[y:y + h, x:x + w]
                    # mrz_rotate = self.__rotate_ex__(mrz,90)
            cv2.imshow('part1',mrz)
            cv2.waitKey(0)
            mrz_rotate = cv2.detailEnhance(mrz, sigma_s=10, sigma_r=0.35)
            cv2.imshow('part1',mrz_rotate)
            cv2.waitKey(0)
            mrzText = pytesseract.image_to_string(mrz_rotate,lang='rus')
            mrzText = mrzText.replace(" ", "")
            return mrzText
        return None
    '''          
            
            
'''
    
    def try_extract_data3(self,img_str):
        
        img = cv2.imread(img_str)
        img =cv2.detailEnhance(img, sigma_s=10, sigma_r=0.45)
        scale_percent = self.__get_resize_scale__(img)
        resized = self.__resize__(img,scale_percent[0],scale_percent[1])
        cv2.imshow('fff',resized)
        cv2.waitKey(0)
        r = self.__rotate_ex__(resized,90)#imutils.rotate_bound(resized, 90)#self.__rotate_ex__(resized,90)
        r = r[int(r.shape[1] / 2):, 0:r.shape[0]]
        gray = cv2.cvtColor(r, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Blackhat", gray)
        cv2.waitKey(0)
        (H, W) = gray.shape
        rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 7))
        sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))

        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)
        cv2.imshow("Blackhat", blackhat)
        cv2.waitKey(0)

        grad = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        grad = np.absolute(grad)
        (minVal, maxVal) = (np.min(grad), np.max(grad))
        grad = (grad - minVal) / (maxVal - minVal)
        grad = (grad * 255).astype("uint8")
        cv2.imshow("Gradient", grad)
        cv2.waitKey(0)

        grad = cv2.morphologyEx(grad, cv2.MORPH_CLOSE, rectKernel)
        thresh = cv2.threshold(grad, 0, 255,
	    cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        cv2.imshow("Rect Close", thresh)
        cv2.waitKey(0)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
        thresh = cv2.erode(thresh, None, iterations=2)
        cv2.imshow("Square Close", thresh)
        cv2.waitKey(0)

        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	    cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sort_contours(cnts, method="top-to-bottom")[0] 
        
        mrzBox_surname = None
        mzrBox_name = None
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            percentWidth = w / float(W) 
            percentHeight = h / float(H)
            print(percentHeight,percentWidth)
           
            pX = int((x + w)*0.03)
            pY = int((y + h)*0.03)
            (x, y) = (x - pX, y - pY)
            (w, h) = (w + (pX * 2), h + (pY * 2))
            if(x<=0 or y<=0):
                continue
            mrz = r[y:y + h, x:x + w]
                # mrz_rotate = self.__rotate_ex__(mrz,90)
            cv2.imshow('part1',mrz)
            cv2.waitKey(0)
            # extract the padded MRZ from the image
            print(y,y+h,x,x+w)
            
            if(percentWidth > 0.15 and percentWidth < 0.17 and percentHeight > 0.01 and percentHeight < 0.02):
                mrzBox_surname = (x,y,w,h)
            if (percentWidth > 0.3 and percentWidth < 0.4 and percentHeight > 0.3 and percentHeight < 0.4):
                mzrBox_name = (x,y,w,h)
            
            ## surname - width - 0.1625 height=0.019
            ## surname -  0.15  height = 0.016
            ## name - width 0.322 height=0.3222
            ## name - wight - 0.26 height=0.14
            ## number = width = 0.024 height=0.143
            ## seria width=0.45 heigh=0.1
            ## number = width = 0.024 height=0.143
            ## seria width=0.45 heigh=0.025

        
        if mrzBox_surname is None or mzrBox_name is None:
            raise Exception('aaaaaa')
        lst = [mzrBox_name,mrzBox_surname]
        for box in lst:
            (x, y, w, h) = box
            print(x,y,w,h)
        
            pX = int((x + w)*0.03)
            pY = int((y + h)*0.03)
            (x, y) = (x - pX, y - pY)
            (w, h) = (w + (pX * 2), h + (pY * 2))
            # extract the padded MRZ from the image
            print(y,y+h,x,x+w)
            if(x<=0 or y<=0):
                raise Exception('aaaaa')
            mrz = r[y:y + h, x:x + w]
       # mrz_rotate = self.__rotate_ex__(mrz,90)
            cv2.imshow('before_improving',mrz)
            cv2.waitKey(0)
            mrz_rotate = cv2.detailEnhance(mrz, sigma_s=10, sigma_r=0.45)
            cv2.imshow('dcdcd',mrz_rotate)
            cv2.waitKey(0)
            mrzText = pytesseract.image_to_string(mrz_rotate,lang='rus')
            mrzText = mrzText.replace(" ", "")
            print(mrzText)
'''
c = ImgProccessor()
#print('here:' + str(c.try_extract_data('chat_672125750/photo.png')))
print('here:' + str(c.try_extract_data('test_img/my.png')))
#print(c.try_get_seria_number('test_img/passport.jpg'))
#c.try_extract_data("test_img/my.png")