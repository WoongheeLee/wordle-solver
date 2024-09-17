import random
import re


class WordleSolver:

    def __init__(self, 
                 path_vocab='../dictionary/full_vocabs.txt',
                 path_unique='../dictionary/unique.txt'
                ):
        self.vocabs = self._get_words(path_vocab)
        self.unique = self._get_words(path_unique)
        self.flag_first = True
        self.no = set() # 절대 안들어가는 알파벳
        self.yes = [None] * 5 # 위치도 맞아떨어지는 알파벳
        self.wrong = set() # 들어가는 알파벳인데 위치 틀림
        self.update_wrong = list()
        self.including = set()

        print('Initialized with', len(self.vocabs), 'words.')
    
    def _get_words(self, fname):
        '''
        args
            fname: (str) 읽어올 파일 경로
        returns
            (list) 단어
        '''
        with open(fname, 'r') as f:
            lines = f.readlines()
            words = [line.strip() for line in lines]
        return words


    def _exclude_letters(self):
        '''
        제외 알파벳 들어가는 단어 빼
        '''
        filtered = set()
        for v in self.vocabs:
            check = True
            for n in self.no:
                if n in v:
                    check = False
                    break
            if check:
                filtered.add(v)
        self.vocabs = sorted(filtered)


    def _match_exact(self):
        '''
        (list) 맞아떨어지는 단어장
        '''
        pattern = '^'
        for y in self.yes:
            if y: 
                pattern += f"{y}"
            else:
                pattern += '.'

        filtered = set()
        for v in self.vocabs:
            if re.match(pattern, v):
                filtered.add(v)

        self.vocabs = sorted(filtered)

    def _filter_misplaced(self):
        '''
        (list) 필터링 후 단어장
        '''
        while True:
            if len(self.update_wrong)==0:
                break
            wrong = self.update_wrong.pop()
            for i, v in enumerate(wrong):
                if v:
                    placeholder = [None] * 5
                    placeholder[i] = v
                    self.wrong.add(tuple(placeholder))
                    self.including.add(v)

        for wrong in self.wrong:
            pattern = '^'
            for w in wrong:
                if w:
                    pattern += w
                else:
                    pattern += '.'

            filtered = set()
            for v in self.vocabs:
                match_flag = True
                if re.match(pattern, v):
                    match_flag = False
                for m in self.including:
                    if m not in v:
                        match_flag = False
                        break
                if match_flag:
                    filtered.add(v)

            self.vocabs = sorted(filtered)


    def _update_exclude(self):
        '''
        args
            no: (set) 절대 안들어가는 알파벳
        '''
        self.no = set(self.no) - set(self.yes)
        [self.no.add(v) for v in self.no]
        self._exclude_letters()
        print('excluding:', sorted(self.no))

    
    def _update_exact(self):
        '''
        args
            yes: (list) 위치 맞아떨어지는 알파벳
        '''
        self._match_exact()

    def _update_misplaced(self):
        ''' 
        args
            wrong: (list) 위치 틀린 알파벳
        '''
        self._filter_misplaced()
    

    def sample_word(self, yes=None, wrong=None, no=None, flag=True, itr=5):
        '''
        정답일 것 같은 단어 추천
        
        args
            yes: (list) 위치 맞아떨어지는 알파벳
            wrong: (list) 위치 틀린데 들어가는 알파벳
            no: (set, list) 절대 안들어가는 알파벳
            flag: (bool) 첫 시도냐(true) 아니냐(false)
            itr: (int) 추천 단어 개수
        '''
        print('sampling...')
        if yes:
            assert len(yes) == 5
        if wrong:
            assert len(wrong) == 5
            
        if yes:
            for i, v in enumerate(yes):
                if yes[i]:
                    self.yes[i] = yes[i]
            self._update_exact()
        if wrong:
            self.update_wrong.append(wrong)
            self._update_misplaced()
        if no:
            self.no = self.no | no
            self._update_exclude()

        solutions = dict()
        suggestions = []

        if self.flag_first and flag:
            # 첫 라운드면
            for _ in range(itr):
                idx = int(random.random() * len(self.unique))
                print(self.unique[idx])
                suggestions.append(self.unique[idx])
            self.flag_first = False
        else:
            print('vocabs:',len(self.vocabs))
            for _ in range(itr):
                idx = int(random.random() * len(self.vocabs))
                print(self.vocabs[idx])
                suggestions.append(self.vocabs[idx])

        print('# of words:', len(self.vocabs))

        solutions['word_nums'] = len(self.vocabs)
        solutions['suggestions'] = suggestions
        return solutions